import sqlite3
import os
from datetime import datetime

AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')

class AuthDatabase:
    def __init__(self):
        self.db_path = AUTH_DB_PATH
        self._initialize_database()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize_database(self):
        """Create users table"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        
        conn.commit()
        conn.close()
    def create_user(self, name, email, password):
        conn = None
        try:
            print(f"Creating user - Name: {name}, Email: {email}")
            conn = self._get_connection()
            print(f"Database connection established: {self.db_path}")
            cursor = conn.cursor()
            
            print(f"Inserting user into database...")
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, password)
            )
            
            user_id = cursor.lastrowid
            print(f"User inserted with ID: {user_id}")
            conn.commit()
            print("Transaction committed")
            
            # Get the created user before closing connection
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            print(f"Fetched user row: {dict(row) if row else None}")
            
            if row:
                return dict(row)
            else:
                print("ERROR: Could not fetch created user!")
                return None
            
        except sqlite3.IntegrityError as e:
            print(f'Integrity error: Email {email} already exists - {e}')
            return None
        except Exception as e:
            print(f'Error creating user: {type(e).__name__}: {e}')
            import traceback
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()
                print("Database connection closed")
    
    
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_users(self):
        """Get all users"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

# Singleton instance
auth_db = AuthDatabase()