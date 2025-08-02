import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    last_active TEXT
)
""")
conn.commit()

def add_or_update_user(user_id, name):
    now = datetime.now().isoformat()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone():
        cur.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
        return False
    else:
        cur.execute("INSERT INTO users (user_id, name, last_active) VALUES (?, ?, ?)", (user_id, name, now))
        conn.commit()
        return True

def get_recent_users(days=15):
    threshold = datetime.now() - timedelta(days=days)
    cur.execute("SELECT user_id, name FROM users WHERE last_active >= ?", (threshold.isoformat(),))
    return cur.fetchall()

def clean_old_users(days=15):
    threshold = datetime.now() - timedelta(days=days)
    cur.execute("DELETE FROM users WHERE last_active < ?", (threshold.isoformat(),))
    conn.commit()
