import sqlite3
from datetime import datetime

DB_PATH = "firewall.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT,
        category TEXT,
        attack_type TEXT,
        risk_level TEXT,
        blocked INTEGER,
        threat_score REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_scan(result: dict, prompt: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO scans (
            prompt, category, attack_type, risk_level,
            blocked, threat_score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        prompt,
        result.get("category"),
        result.get("attack_type"),
        result.get("risk_level"),
        1 if result.get("blocked") else 0,
        result.get("threat_score"),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()