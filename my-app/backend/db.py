"""
SQLite persistence for learning and personalization:
- users: identity for personalization (keyed by email/identifier)
- chat_history: per-user, per-course conversation history
- mistakes: recorded mistakes for weak-area tracking and weekly review
- study_plans: adaptive study plan JSON per user
"""
import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "learning_helper.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_chat_user_course ON chat_history(user_id, course);
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                topic TEXT,
                question TEXT,
                correction TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_mistakes_user_course ON mistakes(user_id, course);
            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                plan_json TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()
    finally:
        conn.close()
    logger.info("Database initialized at %s", DB_PATH)


def get_or_create_user(identifier: str) -> int:
    if not identifier or not identifier.strip():
        raise ValueError("identifier is required")
    conn = get_conn()
    try:
        cur = conn.execute(
            "SELECT id FROM users WHERE identifier = ?",
            (identifier.strip(),),
        )
        row = cur.fetchone()
        if row:
            return row[0]
        cur = conn.execute(
            "INSERT INTO users (identifier) VALUES (?)",
            (identifier.strip(),),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def save_chat_turn(user_id: int, course: str, role: str, content: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO chat_history (user_id, course, role, content) VALUES (?, ?, ?, ?)",
            (user_id, course, role, content[:10000]),  # cap size
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_chat_history(
    user_id: int,
    course: str,
    limit: int = 30,
) -> List[Dict[str, str]]:
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            SELECT role, content FROM chat_history
            WHERE user_id = ? AND course = ?
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, course, limit),
        )
        rows = cur.fetchall()
        out = [{"role": r, "content": c} for r, c in reversed(rows)]
        return out
    finally:
        conn.close()


def get_recent_user_questions(user_id: int, course: str, limit: int = 20) -> List[str]:
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            SELECT content FROM chat_history
            WHERE user_id = ? AND course = ? AND role = 'user'
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, course, limit),
        )
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def _normalize_for_similarity(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t))
    return t


def find_similar_past_question(
    user_id: int,
    course: str,
    current_question: str,
    threshold: float = 0.5,
    max_candidates: int = 10,
) -> Optional[Dict[str, Any]]:
    """Simple token-overlap similarity to detect repeated/similar questions."""
    past = get_recent_user_questions(user_id, course, limit=max_candidates)
    if not past:
        return None
    cur_norm = _normalize_for_similarity(current_question)
    cur_tokens = set(cur_norm.split())
    if not cur_tokens:
        return None
    best_ratio = 0.0
    best_question = None
    for p in past:
        if p.strip() == current_question.strip():
            return {"question": p, "similarity": 1.0, "note": "Same question asked before."}
        p_norm = _normalize_for_similarity(p)
        p_tokens = set(p_norm.split())
        if not p_tokens:
            continue
        overlap = len(cur_tokens & p_tokens) / max(len(cur_tokens), len(p_tokens))
        if overlap > best_ratio and overlap >= threshold:
            best_ratio = overlap
            best_question = p
    if best_question is None:
        return None
    return {"question": best_question, "similarity": best_ratio, "note": "Similar question asked before."}


def get_mistakes(user_id: int, course: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_conn()
    try:
        if course:
            cur = conn.execute(
                """
                SELECT id, course, topic, question, correction, created_at
                FROM mistakes WHERE user_id = ? AND course = ?
                ORDER BY created_at DESC
                """,
                (user_id, course),
            )
        else:
            cur = conn.execute(
                """
                SELECT id, course, topic, question, correction, created_at
                FROM mistakes WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "course": r[1],
                "topic": r[2],
                "question": r[3],
                "correction": r[4],
                "created_at": r[5],
            }
            for r in rows
        ]
    finally:
        conn.close()


def add_mistake(
    user_id: int,
    course: str,
    question: str,
    correction: str = "",
    topic: Optional[str] = None,
) -> int:
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO mistakes (user_id, course, topic, question, correction)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, course, topic or "", question[:2000], correction[:2000]),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_mistake(mistake_id: int, user_id: int) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute(
            "DELETE FROM mistakes WHERE id = ? AND user_id = ?",
            (mistake_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_study_plan(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    try:
        cur = conn.execute(
            "SELECT plan_json, updated_at FROM study_plans WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"plan": json.loads(row[0]), "updated_at": row[1]}
    finally:
        conn.close()


def save_study_plan(user_id: int, plan: Dict[str, Any]) -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO study_plans (user_id, plan_json, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                plan_json = excluded.plan_json,
                updated_at = datetime('now')
            """,
            (user_id, json.dumps(plan)),
        )
        conn.commit()
    finally:
        conn.close()
