import sqlite3
from datetime import datetime
import threading


class PersistentMemory:
    def __init__(self, db_path: str = "memory.db"):
        # ✅ Allow multi-thread usage
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

        self.lock = threading.Lock()

        self._create_table()

    def _create_table(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT
                )
            """)
            self.conn.commit()

    def add(self, role: str, content: str):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO conversation (role, content, timestamp) VALUES (?, ?, ?)",
                (role, content, datetime.utcnow().isoformat())
            )
            self.conn.commit()

    def get_context(self, limit: int = 10) -> str:
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT role, content FROM conversation ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()

        rows.reverse()

        formatted = ""
        for role, content in rows:
            formatted += f"{role.upper()}: {content}\n"

        return formatted.strip()

    def clear(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM conversation")
            self.conn.commit()