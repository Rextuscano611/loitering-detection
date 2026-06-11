import sqlite3
import os
from datetime import datetime
from config import DB_PATH


class DBHandler:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()
        print(f"[DBHandler] Connected to {DB_PATH}")

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS loiter_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id    INTEGER,
                zone_name   TEXT,
                duration_s  REAL,
                snapshot    TEXT,
                timestamp   TEXT
            )
        """)
        self.conn.commit()

    def log_event(self, track_id, zone_name, duration_s, snapshot_path=None):
        """Log a loitering event to the database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("""
            INSERT INTO loiter_events (track_id, zone_name, duration_s, snapshot, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (track_id, zone_name, round(duration_s, 2), snapshot_path, timestamp))
        self.conn.commit()
        print(f"[DBHandler] Event logged — ID:{track_id} | Zone:{zone_name} | {duration_s:.1f}s")

    def get_recent_events(self, limit=20):
        """Fetch recent loitering events."""
        cursor = self.conn.execute("""
            SELECT track_id, zone_name, duration_s, snapshot, timestamp
            FROM loiter_events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()