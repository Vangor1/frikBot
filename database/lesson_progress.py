import sqlite3
from datetime import datetime

from .db import DB_PATH


def add_lesson_progress(reminder_id: int, user_id: int, text: str, score: int | None):
    """
    Сохраняет отчет о занятии пользователя.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO lesson_progress(reminder_id, user_id,
        progress_text, progress_value, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (reminder_id, user_id, text, score, now),
    )
    conn.commit()
    conn.close()
