import sqlite3
from datetime import datetime

class MessageDB:
    def __init__(self, db_path="messages.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT,
                    author_id TEXT,
                    author_name TEXT,
                    author_display_name TEXT,
                    content TEXT,
                    timestamp TEXT
                )
            """)

    def add_message(self, channel_id, author_id, author_name, author_display_name, content, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                INSERT INTO messages (channel_id, author_id, author_name, author_display_name, content, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (channel_id, author_id, author_name, author_display_name, content, timestamp))

    def get_messages(self, channel_id=None, limit=100): # limit is the number of messages to return
        cursor = self.conn.cursor()
        if channel_id:
            cursor.execute("""
                SELECT * FROM messages WHERE channel_id = ? ORDER BY timestamp DESC LIMIT ?
            """, (channel_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        return cursor.fetchall()
