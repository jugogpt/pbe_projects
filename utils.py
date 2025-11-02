import os
import sqlite3
import time


def ensure_folders():
    """Create necessary directories for data, recordings, screenshots, transcripts, and workflows if they don't exist."""
    os.makedirs("data/recordings", exist_ok=True)
    os.makedirs("data/screenshots", exist_ok=True)
    os.makedirs("data/transcripts", exist_ok=True)
    os.makedirs("data/workflows", exist_ok=True)
    os.makedirs("data/analyses", exist_ok=True)


def timestamped_filename():
    """Generate a timestamped filename for recordings."""
    return time.strftime("recording_%Y%m%d_%H%M%S")


def init_db():
    """Initialize SQLite database with usage table."""
    conn = sqlite3.connect("data/usage.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app TEXT,
            seconds REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn