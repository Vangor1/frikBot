import sqlite3
from datetime import datetime

from .db import DB_PATH


def set_user_section_grade(user_id: int, section_id: int, grade: int):
    """
    Ставит или обновляет оценку пользователя за конкретный раздел.
    Если оценка уже есть — обновляет; если нет — добавляет.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "SELECT id FROM user_section_grades WHERE user_id=? AND section_id=?",
        (user_id, section_id),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            """
            UPDATE user_section_grades
            SET grade=?, updated_at=?
            WHERE user_id=? AND section_id=?
            """,
            (grade, now, user_id, section_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO user_section_grades (user_id, section_id, grade, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, section_id, grade, now),
        )
    conn.commit()
    conn.close()


def get_average_grade(user_id: int, section_id: int):
    """
    Возвращает среднюю оценку пользователя по всем темам в разделе.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT AVG(utg.grade)
        FROM topics t
        LEFT JOIN user_topic_grades utg
        ON utg.topic_id = t.id AND utg.user_id = ?
        WHERE t.section_id = ?
        """,
        (user_id, section_id),
    )
    average = cursor.fetchone()[0]
    conn.close()
    return average if average is not None else None


def get_average_grade_for_stage(user_id: int, stage_id: int):
    """
    Возвращает среднюю оценку пользователя по всем темам этапа.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT AVG(utg.grade)
        FROM topics t
        INNER JOIN sections s ON t.section_id = s.id
        LEFT JOIN user_topic_grades utg
            ON utg.topic_id = t.id AND utg.user_id = ?
        WHERE s.stage_id = ?
        """,
        (user_id, stage_id),
    )
    average = cursor.fetchone()[0]
    conn.close()
    return average if average is not None else None
