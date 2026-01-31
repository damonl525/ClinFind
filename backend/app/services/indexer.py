import os
import time
import logging
from ..core.database import get_db_connection
from .parser_factory import ParserFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self):
        pass

    def clear_all(self):
        """Clear all indexed data."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM search_index")
            cursor.execute("DELETE FROM files")
            conn.commit()
            logger.info("Index cleared.")
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
        finally:
            conn.close()

    def index_path(self, path: str):
        """
        Index a folder or a single file.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            logger.error(f"Path not found: {path}")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        if os.path.isfile(path):
            logger.info(f"Indexing single file: {path}")
            try:
                if self._needs_indexing(cursor, path):
                    self._index_file(cursor, path)
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to index {path}: {e}")
                self._mark_failed(cursor, path, str(e))
                conn.commit() # Ensure error status is saved
        else:
            self.index_folder(path)
        
        conn.close()

    def index_folder(self, folder_path: str):
        """
        Recursively scan and index supported files in the folder.
        This is a blocking operation, designed to be run in a background task.
        """
        folder_path = os.path.abspath(folder_path)
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return

        logger.info(f"Starting index for: {folder_path}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 1. Check if file needs indexing (modified time)
                if self._needs_indexing(cursor, file_path):
                    try:
                        self._index_file(cursor, file_path)
                        count += 1
                        if count % 10 == 0:
                            conn.commit() # Commit every 10 files
                    except Exception as e:
                        logger.error(f"Failed to index {file_path}: {e}")
                        self._mark_failed(cursor, file_path, str(e))
        
        conn.commit()
        conn.close()
        logger.info(f"Indexing complete. Indexed {count} files.")

    def _needs_indexing(self, cursor, file_path: str) -> bool:
        """Check if file is new or modified since last index."""
        try:
            stat = os.stat(file_path)
            last_modified = stat.st_mtime
            file_size = stat.st_size
        except FileNotFoundError:
            return False

        cursor.execute("SELECT last_modified, file_size FROM files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        
        if row:
            # File exists, check if modified
            # Floating point comparison with small tolerance
            if abs(row['last_modified'] - last_modified) > 1 or row['file_size'] != file_size:
                return True
            return False
        else:
            # New file
            return True

    def _index_file(self, cursor, file_path: str):
        """Parse file and update database."""
        parser = ParserFactory.get_parser(file_path)
        if not parser:
            return # Unsupported type

        logger.info(f"Indexing: {file_path}")
        
        # 1. Parse content
        content, keywords = parser.parse(file_path)
        
        if not content:
             logger.warning(f"No content extracted from {file_path}")
        
        stat = os.stat(file_path)
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1].lower().replace('.', '')
        
        # 2. Update 'files' table
        cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        
        if row:
            # Update existing
            cursor.execute("""
                UPDATE files 
                SET last_modified = ?, file_size = ?, file_type = ?, indexed_status = 1, error_message = NULL
                WHERE file_path = ?
            """, (stat.st_mtime, stat.st_size, file_type, file_path))
            
            # Update FTS index (Delete then Insert is safer for FTS)
            cursor.execute("DELETE FROM search_index WHERE file_path = ?", (file_path,))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO files (file_path, last_modified, file_size, file_type, indexed_status)
                VALUES (?, ?, ?, ?, 1)
            """, (file_path, stat.st_mtime, stat.st_size, file_type))
            
        # 3. Insert into FTS index
        cursor.execute("""
            INSERT INTO search_index (file_path, title, content, keywords)
            VALUES (?, ?, ?, ?)
        """, (file_path, file_name, content, keywords))

    def _mark_failed(self, cursor, file_path: str, error_msg: str):
        """Mark file as failed in database."""
        # Check if row exists first to decide UPDATE or INSERT
        cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
        if cursor.fetchone():
             cursor.execute("UPDATE files SET indexed_status = 2, error_message = ? WHERE file_path = ?", (error_msg, file_path))
        else:
             # Try to get stat if possible, else defaults
             try:
                 stat = os.stat(file_path)
                 lm = stat.st_mtime
                 sz = stat.st_size
             except:
                 lm = 0
                 sz = 0
             
             cursor.execute("""
                INSERT INTO files (file_path, last_modified, file_size, indexed_status, error_message)
                VALUES (?, ?, ?, 2, ?)
            """, (file_path, lm, sz, error_msg))
