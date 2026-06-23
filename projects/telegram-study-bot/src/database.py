from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    conn.commit()


def add_task(conn: sqlite3.Connection, user_id: int, title: str) -> int:
    cur = conn.execute('INSERT INTO tasks(user_id, title) VALUES (?, ?)', (user_id, title.strip()))
    conn.commit()
    return int(cur.lastrowid)


def list_tasks(conn: sqlite3.Connection, user_id: int) -> list[sqlite3.Row]:
    return list(conn.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY is_done, id', (user_id,)))


def mark_done(conn: sqlite3.Connection, user_id: int, task_id: int) -> bool:
    cur = conn.execute('UPDATE tasks SET is_done = 1 WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    return cur.rowcount > 0
