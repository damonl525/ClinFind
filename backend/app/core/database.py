import os
import sqlite3
import sys
from pathlib import Path

# Define database path
# In development: ./search_index.db
# In production: %APPDATA%/FileSearcher/search_index.db or local folder
if getattr(sys, 'frozen', False):
    # Production mode
    APP_DATA = os.path.join(os.getenv('APPDATA'), 'FileSearcher')
    os.makedirs(APP_DATA, exist_ok=True)
    DB_PATH = os.path.join(APP_DATA, 'search_index.db')
else:
    # Development mode
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'search_index.db')

def get_db_connection():
    """Create a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables."""
    print(f"Initializing database at: {DB_PATH}")
    conn = get_db_connection()
    
    # Enable WAL mode for better concurrency (Search while Indexing)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    cursor = conn.cursor()
    
    # Enable FTS5 extension if not enabled (usually built-in)
    # Windows Python usually has FTS5 enabled by default.
    
    # 1. Files metadata table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE NOT NULL,
        last_modified REAL,
        file_size INTEGER,
        file_type TEXT,
        indexed_status INTEGER DEFAULT 0, -- 0: Pending, 1: Indexed, 2: Failed
        error_message TEXT
    )
    ''')
    
    # 2. FTS5 Search Index table
    # Trigram tokenizer is good for substring matching
    try:
        cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
            file_path UNINDEXED,
            title,
            content,
            keywords,
            tokenize = 'trigram'
        )
        ''')
    except sqlite3.OperationalError as e:
        print(f"Warning: FTS5 might not be supported or trigram tokenizer missing. Fallback to standard tokenizer. Error: {e}")
        # Fallback to standard tokenizer if trigram is missing
        cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
            file_path UNINDEXED,
            title,
            content,
            keywords
        )
        ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
