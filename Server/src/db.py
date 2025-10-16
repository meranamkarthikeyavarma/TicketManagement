import sqlite3
import os
from datetime import datetime
import random
import string

# Database paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'app.db')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign keys
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('LOW','MEDIUM','HIGH')),
            status TEXT NOT NULL CHECK(status IN ('OPEN','IN_PROGRESS','CLOSED')),
            reporter TEXT NOT NULL,
            projectId TEXT
        );

        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            createdAt TEXT NOT NULL,
            author TEXT NOT NULL,
            body TEXT NOT NULL,
            ticketId TEXT NOT NULL,
            FOREIGN KEY(ticketId) REFERENCES tickets(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parentProject TEXT NOT NULL,
            createdAt TEXT NOT NULL
        );
    ''')
    
    conn.commit()
    conn.close()
    print('✅ Database initialized')

def generate_id():
    """Generate unique ID similar to TypeScript version"""
    timestamp = int(datetime.now().timestamp() * 1000)
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{timestamp}_{random_str}"

def row_to_dict(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)