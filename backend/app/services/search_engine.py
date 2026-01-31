import re
import os
from ..core.database import get_db_connection
from .fuzzy_matcher import FuzzySearchEngine
from .search_precision import SearchPrecisionController, PrecisionLevel

class SearchEngine:
    def __init__(self):
        self.fuzzy_engine = FuzzySearchEngine()
        self.precision_controller = SearchPrecisionController()

    def _highlight_metadata(self, text: str) -> str:
        """Wrap metadata tags in span for styling."""
        # Pattern: [Page:1], [Sheet:Sheet1...], [Slide:1], [Para:1], [Table:1...]
        pattern = r'(\[(?:Page|Sheet|Row|Col|Slide|Para|Table).*?\])'
        return re.sub(pattern, r'<span class="meta">\1</span>', text)

    def _parse_logical_query(self, query: str) -> tuple[str, list[str]]:
        """
        解析逻辑查询语法 (AND/OR)
        返回: (operator, terms_list)
        """
        query = query.strip()
        
        # 检查是否包含 AND 或 OR (大小写不敏感)
        # 优先处理 AND（更严格）
        if re.search(r'\s+AND\s+', query, re.IGNORECASE):
            terms = re.split(r'\s+AND\s+', query, flags=re.IGNORECASE)
            return ('AND', [t.strip() for t in terms if t.strip()])
        elif re.search(r'\s+OR\s+', query, re.IGNORECASE):
            terms = re.split(r'\s+OR\s+', query, flags=re.IGNORECASE)
            return ('OR', [t.strip() for t in terms if t.strip()])
        else:
            return ('NONE', [query])

    def search(self, query: str, limit: int = 50, precision: str = "medium", paths: list[str] = None):
        """
        Perform full-text search using SQLite FTS5 with V2.1 logic integration.
        Supports AND/OR logical operators.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 解析逻辑查询
        operator, query_terms = self._parse_logical_query(query)
        logger.info(f"Logical operator: {operator}, terms: {query_terms}")
        
        # 标准化路径以匹配数据库中的格式
        normalized_paths = None
        if paths:
            normalized_paths = [os.path.normpath(os.path.abspath(p)) for p in paths]
            logger.info(f"Search paths normalized: {normalized_paths}")

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查数据库是否有数据
        cursor.execute("SELECT COUNT(*) as total FROM search_index")
        total_records = cursor.fetchone()['total']
        logger.info(f"Total records in search_index: {total_records}")
        
        if total_records == 0:
            logger.warning("Search index is empty!")
            conn.close()
            return []
        
        # 对于 AND 查询，需要特殊处理
        if operator == 'AND':
            return self._search_with_and(cursor, query_terms, limit, conn, normalized_paths, precision)
        elif operator == 'OR':
            return self._search_with_or(cursor, query_terms, limit, conn, normalized_paths, precision)
        
        # 单一查询词的原有逻辑
        query = query_terms[0]
        
        # Check if we should use LIKE fallback for short CJK queries
        # Trigram tokenizer fails to MATCH terms < 3 chars
        use_like_fallback = self._is_short_cjk(query)
        logger.info(f"Using LIKE fallback: {use_like_fallback}")
        
        if use_like_fallback:
            return self._search_with_like(cursor, query, limit, conn, normalized_paths)

        # 1. Expand Query (V2.1 Logic)
        # Only expand if precision is NOT exact
        search_terms = [query]
        if precision != PrecisionLevel.EXACT:
            expanded_terms = self.fuzzy_engine.expand_query(query)
            # Limit expansion to avoid overly complex queries
            search_terms = list(expanded_terms)[:5] 
        
        logger.info(f"Search terms: {search_terms}")
        
        # 2. Construct FTS Query
        fts_query_parts = []
        for term in search_terms:
            words = term.strip().split()
            word_parts = []
            for word in words:
                clean_word = word.replace('"', '""')
                word_parts.append(f'"{clean_word}"*')
            
            if word_parts:
                fts_query_parts.append(f"({' AND '.join(word_parts)})")
        
        fts_query_str = " OR ".join(fts_query_parts)
        logger.info(f"FTS query: {fts_query_str}")
        
        # 3. Execute Search - 增加snippet长度以包含位置信息
        base_sql = """
        SELECT 
            file_path, 
            title, 
            snippet(search_index, 2, '<b>', '</b>', '...', 64) as highlight,
            rank
        FROM search_index 
        WHERE search_index MATCH ? 
        """
        
        params = [fts_query_str]
        
        # Add path filtering if provided
        if normalized_paths:
            path_clauses = []
            for path in normalized_paths:
                # Use LIKE for path prefix matching (Case Insensitive)
                path_clauses.append("LOWER(file_path) LIKE ?")
                params.append(f"{path.lower()}%")
            
            if path_clauses:
                base_sql += f" AND ({' OR '.join(path_clauses)})"
                logger.info(f"Added path filtering: {path_clauses}")
        
        base_sql += " ORDER BY rank LIMIT ?"
        params.append(limit * 2)
        
        logger.info(f"Final SQL: {base_sql}")
        logger.info(f"SQL params: {params}")
        
        try:
            cursor.execute(base_sql, tuple(params)) 
            raw_results = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Raw results count: {len(raw_results)}")
        except Exception as e:
            logger.error(f"Search error: {e}")
            conn.close()
            return []
        
        conn.close()
        
        # 4. Filter Results and enhance with location info
        filtered_results = []
        for res in raw_results:
            # Highlight metadata tags in the snippet
            res['highlight'] = self._highlight_metadata(res['highlight'])
            
            content_snippet = res['highlight'].replace('<b>', '').replace('</b>', '')
            if self.precision_controller.is_content_quality_acceptable(content_snippet):
                filtered_results.append(res)
        
        logger.info(f"Filtered results count: {len(filtered_results)}")
        return filtered_results[:limit]

    def _is_short_cjk(self, term: str) -> bool:
        """Check if term is short CJK which fails with trigram MATCH."""
        term = term.strip()
        if not term:
            return False
        # If length is >= 3, trigram should handle it (or scan it correctly)
        # But specifically for 1-2 char CJK, it fails often with MATCH
        if len(term) >= 3:
            return False
            
        # Check for CJK characters
        for char in term:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False

    def _search_with_like(self, cursor, query: str, limit: int, conn, paths: list[str] = None, close_conn: bool = True):
        """Fallback search using LIKE for short CJK terms."""
        try:
            # Search in content OR title
            # We select content to generate snippet manually
            base_sql = """
            SELECT file_path, title, content 
            FROM search_index 
            WHERE (content LIKE ? OR title LIKE ?) 
            """
            
            wildcard_query = f"%{query}%"
            params = [wildcard_query, wildcard_query]
            
            # Add path filtering if provided
            if paths:
                path_clauses = []
                for path in paths:
                    path_clauses.append("LOWER(file_path) LIKE ?")
                    params.append(f"{path.lower()}%")
                
                if path_clauses:
                    base_sql += f" AND ({' OR '.join(path_clauses)})"
            
            base_sql += " LIMIT ?"
            params.append(limit)
            
            cursor.execute(base_sql, tuple(params))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                content = row['content'] or ""
                title = row['title'] or ""
                snippet = self._generate_snippet(content, query)
                snippet = self._highlight_metadata(snippet)
                
                # Calculate pseudo-rank (higher count = better)
                # FTS5 returns negative for better rank (usually). 
                # Let's return negative count to match "lower is better" convention.
                q_lower = query.lower()
                c_count = content.lower().count(q_lower)
                t_count = title.lower().count(q_lower)
                score = c_count + (t_count * 5) # Weighted score
                
                results.append({
                    'file_path': row['file_path'],
                    'title': row['title'],
                    'highlight': snippet,
                    'rank': -score  # Negative score for sorting
                })
            
            # Sort by rank (ascending, so more negative is first)
            results.sort(key=lambda x: x['rank'])
            
            conn.close() if close_conn else None
            return results
        except Exception as e:
            print(f"LIKE Search error: {e}")
            if close_conn:
                conn.close()
            return []

    def _generate_snippet(self, content: str, query: str, context: int = 100) -> str:
        """Generate snippet with location metadata preserved."""
        if not content:
            return ""
        
        # Find the query in content (case insensitive)
        idx = content.lower().find(query.lower())
        if idx == -1:
            # Maybe match in title? Return start of content
            return content[:context*2] + "..."
        
        # Try to include location metadata before the match
        # Look backwards for the nearest [Slide:X] or similar tag
        start = max(0, idx - context)
        
        # Search backwards from match position to find location tag
        location_pattern = r'\[(Page|Sheet|Row|Col|Slide|Para|Table):[^\]]+\]'
        before_match = content[:idx]
        location_matches = list(re.finditer(location_pattern, before_match))
        
        if location_matches:
            # Get the last location tag before the match
            last_location = location_matches[-1]
            # Start from the location tag if it's within reasonable distance
            if idx - last_location.start() < context * 2:
                start = last_location.start()
        
        end = min(len(content), idx + len(query) + context)
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        # Highlight the query (case insensitive)
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        snippet = pattern.sub(lambda m: f"<b>{m.group()}</b>", snippet)
        
        return snippet

    def _search_with_and(self, cursor, terms: list[str], limit: int, conn, paths: list[str], precision: str):
        """
        AND 逻辑搜索：所有词必须同时出现在同一文档中
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not terms:
            conn.close()
            return []
        
        # 对每个词分别搜索，然后取交集
        term_results = []
        for term in terms:
            use_like = self._is_short_cjk(term)
            if use_like:
                results = self._search_with_like(cursor, term, 200, conn, paths, close_conn=False)
            else:
                # 构建单词 FTS 查询
                clean_term = term.replace('"', '""')
                fts_query = f'"{clean_term}"*'
                
                sql = """
                SELECT file_path, title, file_type,
                       snippet(search_index, 3, '<b>', '</b>', '...', 50) as highlight,
                       rank
                FROM search_index
                WHERE content MATCH ?
                ORDER BY rank
                LIMIT 200
                """
                try:
                    cursor.execute(sql, (fts_query,))
                    results = [dict(row) for row in cursor.fetchall()]
                except:
                    results = self._search_with_like(cursor, term, 200, conn, paths, close_conn=False)
            
            # 仅保留文件路径集合
            file_paths = set(r['file_path'] for r in results)
            term_results.append((file_paths, {r['file_path']: r for r in results}))
        
        if not term_results:
            conn.close()
            return []
        
        # 取所有词结果的交集
        common_paths = term_results[0][0]
        for paths_set, _ in term_results[1:]:
            common_paths = common_paths & paths_set
        
        # 从第一个词的结果中获取详细信息
        final_results = []
        result_dict = term_results[0][1]
        for path in common_paths:
            if path in result_dict:
                result = result_dict[path].copy()
                # 高亮所有搜索词
                for term in terms:
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    result['highlight'] = pattern.sub(
                        lambda m: f'<b>{m.group()}</b>', 
                        result.get('highlight', '')
                    )
                final_results.append(result)
        
        conn.close()
        return final_results[:limit]

    def _search_with_or(self, cursor, terms: list[str], limit: int, conn, paths: list[str], precision: str):
        """
        OR 逻辑搜索：任一词出现即可，结果合并去重
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not terms:
            conn.close()
            return []
        
        all_results = {}
        
        for term in terms:
            use_like = self._is_short_cjk(term)
            if use_like:
                results = self._search_with_like(cursor, term, limit, conn, paths, close_conn=False)
            else:
                clean_term = term.replace('"', '""')
                fts_query = f'"{clean_term}"*'
                
                sql = """
                SELECT file_path, title, file_type,
                       snippet(search_index, 3, '<b>', '</b>', '...', 50) as highlight,
                       rank
                FROM search_index
                WHERE content MATCH ?
                ORDER BY rank
                LIMIT ?
                """
                try:
                    cursor.execute(sql, (fts_query, limit))
                    results = [dict(row) for row in cursor.fetchall()]
                except:
                    results = self._search_with_like(cursor, term, limit, conn, paths, close_conn=False)
            
            # 合并结果，避免重复
            for r in results:
                path = r['file_path']
                if path not in all_results:
                    all_results[path] = r
                else:
                    # 合并高亮
                    existing = all_results[path]
                    if len(r.get('highlight', '')) > len(existing.get('highlight', '')):
                        existing['highlight'] = r['highlight']
        
        # 按 rank 排序
        final_results = list(all_results.values())
        final_results.sort(key=lambda x: x.get('rank', 0))
        
        conn.close()
        return final_results[:limit]