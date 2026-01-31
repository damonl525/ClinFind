from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import uvicorn
import sys
import os
from typing import List, Optional

# Import services
# Ensure app path is in sys.path if running as script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db
from app.services.indexer import Indexer
from app.services.search_engine import SearchEngine
from app.services.ai_client import AIClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    init_db()
    yield
    # Clean up resources on shutdown if needed

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local desktop app flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FolderRequest(BaseModel):
    folder_path: str

class PathRequest(BaseModel):
    path: str

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 50

class AIConfig(BaseModel):
    base_url: str
    api_key: str
    model: str = "gpt-3.5-turbo"

class AIExplainRequest(BaseModel):
    code_snippet: str
    context: str = "code"
    config: AIConfig

@app.get("/")
def read_root():
    return {"Hello": "World", "Service": "FileSearcher Backend v3"}

@app.get("/health")
def health_check():
    return {"status": "ok", "python_version": sys.version}

@app.get("/debug/stats")
def get_debug_stats():
    """获取数据库统计信息用于诊断"""
    from app.core.database import DB_PATH, get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 统计索引文件数
        cursor.execute("SELECT COUNT(*) as total FROM files")
        file_count = cursor.fetchone()['total']
        
        # 统计搜索索引数
        cursor.execute("SELECT COUNT(*) as total FROM search_index")
        index_count = cursor.fetchone()['total']
        
        # 获取路径样本
        cursor.execute("SELECT file_path FROM files LIMIT 10")
        sample_paths = [row['file_path'] for row in cursor.fetchall()]
        
        # 获取文件类型统计
        cursor.execute("SELECT file_type, COUNT(*) as count FROM files GROUP BY file_type")
        file_types = {row['file_type']: row['count'] for row in cursor.fetchall()}
        
        # 检查数据库文件大小
        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        
        return {
            "status": "ok",
            "database": {
                "path": DB_PATH,
                "size_mb": round(db_size / 1024 / 1024, 2),
                "exists": os.path.exists(DB_PATH)
            },
            "statistics": {
                "file_count": file_count,
                "index_count": index_count,
                "file_types": file_types
            },
            "sample_paths": sample_paths
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database": {
                "path": DB_PATH if 'DB_PATH' in locals() else "Unknown",
                "exists": os.path.exists(DB_PATH) if 'DB_PATH' in locals() else False
            }
        }
    finally:
        conn.close()

class RebuildRequest(BaseModel):
    paths: List[str]

@app.post("/index/rebuild")
async def rebuild_index(request: RebuildRequest, background_tasks: BackgroundTasks):
    """
    Clear index and rebuild for provided paths.
    """
    indexer = Indexer()
    indexer.clear_all()
    
    for path in request.paths:
        if os.path.exists(path):
             # Determine if it's a file or folder
             if os.path.isfile(path):
                 background_tasks.add_task(indexer.index_path, path)
             else:
                 background_tasks.add_task(indexer.index_folder, path)
    
    return {"status": "rebuild_started", "paths_count": len(request.paths)}

class IndexStatusRequest(BaseModel):
    paths: List[str]

@app.post("/index/status")
async def get_index_status(request: IndexStatusRequest):
    """
    查询多个路径的索引状态
    返回每个路径是否已索引、索引文件数量
    """
    from app.core.database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = []
    for path in request.paths:
        path = os.path.normpath(os.path.abspath(path))
        
        # 查询该路径下已索引的文件数
        cursor.execute("""
            SELECT COUNT(*) as count FROM files 
            WHERE file_path LIKE ? AND indexed_status = 1
        """, (path + '%',))
        indexed_count = cursor.fetchone()['count']
        
        # 判断索引状态
        if indexed_count > 0:
            status = 'indexed'
        else:
            status = 'not_indexed'
        
        results.append({
            'path': path,
            'status': status,
            'indexed_count': indexed_count
        })
    
    conn.close()
    return {"results": results}

class BatchIndexRequest(BaseModel):
    paths: List[str]

@app.post("/index/batch")
async def batch_index(request: BatchIndexRequest):
    """
    批量索引多个路径（同步执行，增量更新）
    只对新增或修改的文件建立索引
    """
    import logging
    logger = logging.getLogger(__name__)
    
    from app.core.database import get_db_connection
    
    # 获取索引前的记录数
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM search_index")
    before_count = cursor.fetchone()['count']
    conn.close()
    
    indexer = Indexer()
    indexed_paths = []
    
    for path in request.paths:
        if os.path.exists(path):
            logger.info(f"Batch indexing: {path}")
            try:
                indexer.index_path(path)
                indexed_paths.append(path)
            except Exception as e:
                logger.error(f"Failed to index {path}: {e}")
    
    # 获取索引后的记录数
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM search_index")
    after_count = cursor.fetchone()['count']
    conn.close()
    
    new_indexed = after_count - before_count
    
    return {
        "status": "completed",
        "paths_processed": len(indexed_paths),
        "new_files_indexed": new_indexed,
        "total_indexed": after_count
    }

class DeleteIndexRequest(BaseModel):
    path: str

@app.post("/index/delete")
async def delete_index(request: DeleteIndexRequest):
    """
    删除指定路径的索引数据
    """
    import logging
    logger = logging.getLogger(__name__)
    
    from app.core.database import get_db_connection
    
    path = os.path.normpath(os.path.abspath(request.path))
    logger.info(f"Deleting index for path: {path}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 统计要删除的记录数
        cursor.execute("""
            SELECT COUNT(*) as count FROM files 
            WHERE file_path LIKE ?
        """, (path + '%',))
        delete_count = cursor.fetchone()['count']
        
        # 从 files 表删除
        cursor.execute("DELETE FROM files WHERE file_path LIKE ?", (path + '%',))
        
        # 从 search_index 表删除
        cursor.execute("DELETE FROM search_index WHERE file_path LIKE ?", (path + '%',))
        
        conn.commit()
        logger.info(f"Deleted {delete_count} indexed files for path: {path}")
        
        return {
            "status": "completed",
            "path": path,
            "deleted_count": delete_count
        }
    except Exception as e:
        logger.error(f"Failed to delete index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/index/path")
async def index_path(request: PathRequest):
    """
    Synchronously index a path (file or folder) and return results.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(request.path):
        raise HTTPException(status_code=404, detail="Path not found")
    
    logger.info(f"Starting indexing for path: {request.path}")
    
    # 获取索引前的记录数
    from app.core.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM search_index")
    before_count = cursor.fetchone()['count']
    conn.close()
    
    # 同步执行索引
    try:
        indexer = Indexer()
        indexer.index_path(request.path)
        
        # 获取索引后的记录数
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM search_index")
        after_count = cursor.fetchone()['count']
        conn.close()
        
        indexed_count = after_count - before_count
        logger.info(f"Indexing completed: {indexed_count} new files indexed")
        
        return {
            "status": "completed",
            "path": request.path,
            "indexed_count": indexed_count,
            "total_count": after_count
        }
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.post("/index/folder")
async def index_folder(request: FolderRequest):
    """
    Synchronously index a folder and return results.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(request.folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    logger.info(f"Starting indexing for folder: {request.folder_path}")
    
    # 获取索引前的记录数
    from app.core.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM search_index")
    before_count = cursor.fetchone()['count']
    conn.close()
    
    # 同步执行索引
    try:
        indexer = Indexer()
        indexer.index_folder(request.folder_path)
        
        # 获取索引后的记录数
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM search_index")
        after_count = cursor.fetchone()['count']
        conn.close()
        
        indexed_count = after_count - before_count
        logger.info(f"Indexing completed: {indexed_count} new files indexed")
        
        return {
            "status": "completed",
            "folder": request.folder_path,
            "indexed_count": indexed_count,
            "total_count": after_count
        }
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.get("/search")
def search(q: str, limit: int = 50, offset: int = 0, precision: str = "medium", paths: Optional[List[str]] = Query(None)):
    """
    Search for files with pagination support.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not q:
        return {"results": [], "total_count": 0, "has_more": False}
    
    # 记录搜索请求
    logger.info(f"Search request: query='{q}', limit={limit}, offset={offset}, precision='{precision}', paths={paths}")
    
    # 标准化路径
    normalized_paths = None
    if paths:
        normalized_paths = [os.path.normpath(os.path.abspath(p)) for p in paths]
        logger.info(f"Normalized paths: {normalized_paths}")
        
    engine = SearchEngine()
    # 获取更多结果用于计算总数
    all_results = engine.search(q, limit + offset + 1, precision, normalized_paths)
    
    total_count = len(all_results)
    has_more = total_count > offset + limit
    
    # 应用分页
    paginated_results = all_results[offset:offset + limit]
    
    logger.info(f"Search completed: {len(paginated_results)} results returned (total: {total_count})")
    
    return {
        "results": paginated_results,
        "total_count": total_count,
        "has_more": has_more
    }

@app.post("/ai/explain")
async def explain_code(request: AIExplainRequest):
    """
    Explain code using AI.
    """
    client = AIClient(
        base_url=request.config.base_url,
        api_key=request.config.api_key,
        model=request.config.model
    )
    
    explanation = await client.explain_code(request.code_snippet, request.context)
    return {"explanation": explanation}

class AITestRequest(BaseModel):
    base_url: str
    api_key: str
    model: str

@app.post("/ai/test")
async def test_ai_connection(request: AITestRequest):
    """
    Test AI API connection.
    """
    client = AIClient(
        base_url=request.base_url,
        api_key=request.api_key,
        model=request.model
    )
    
    return await client.test_connection()

class AIExpandRequest(BaseModel):
    query: str
    config: AIConfig
    prompt: Optional[str] = None  # 用户自定义的提示词

@app.post("/ai/expand")
async def expand_query(request: AIExpandRequest):
    """
    Expand search query using AI.
    """
    client = AIClient(
        base_url=request.config.base_url,
        api_key=request.config.api_key,
        model=request.config.model
    )
    
    expanded_terms = await client.expand_query(request.query, request.prompt)
    return {"original": request.query, "expanded": expanded_terms}

@app.get("/search/suggestions")
def get_search_suggestions(q: str = ""):
    """
    Get search suggestions based on query and history.
    """
    from app.core.database import get_db_connection
    
    if not q or len(q) < 2:
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    suggestions = []
    
    try:
        # 1. 从文件名中获取建议
        cursor.execute("""
            SELECT DISTINCT title 
            FROM search_index 
            WHERE title LIKE ? 
            LIMIT 5
        """, (f"%{q}%",))
        
        for row in cursor.fetchall():
            suggestions.append({
                "text": row['title'],
                "type": "filename",
                "source": "文件名"
            })
        
        # 2. 从内容中获取常见词汇
        cursor.execute("""
            SELECT file_path, snippet(search_index, 2, '', '', '...', 10) as snippet
            FROM search_index 
            WHERE content MATCH ? 
            LIMIT 3
        """, (f'"{q}"*',))
        
        for row in cursor.fetchall():
            suggestions.append({
                "text": q,
                "type": "content",
                "source": f"来自: {os.path.basename(row['file_path'])}",
                "preview": row['snippet']
            })
            
    except Exception as e:
        print(f"Suggestion error: {e}")
    finally:
        conn.close()
    
    return suggestions[:8]  # 限制返回数量

@app.get("/files/recent")
def get_recent_files(limit: int = 10):
    """
    Get recently indexed files.
    """
    from app.core.database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT file_path, last_modified, file_type
            FROM files 
            WHERE indexed_status = 1
            ORDER BY last_modified DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            # 从文件路径提取文件名作为title
            file_name = os.path.basename(row['file_path'])
            results.append({
                "file_path": row['file_path'],
                "title": file_name,
                "last_modified": row['last_modified'],
                "file_type": row['file_type']
            })
        
        return results
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    # Allow passing port as argument
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
            
    print(f"Starting backend on port {port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
