import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


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


def get_user_section_grade(user_id: int, section_id: int):
    """
    Возвращает (grade, updated_at) — оценку пользователя по разделу и дату обновления.
    Если оценки нет — возвращает None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT grade, updated_at
        FROM user_section_grades
        WHERE user_id=? AND section_id=?
        """,
        (user_id, section_id),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def get_user_grades_by_topic(user_id: int, topic_id: int):
    """
    Возвращает список оценок пользователя по всем разделам темы:
    (section_id, section_name, grade, updated_at)
    Если по какому-то разделу нет оценки — grade будет None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.id, s.name, usg.grade, usg.updated_at
        FROM sections s
        LEFT JOIN user_section_grades usg
        ON s.id = usg.section_id AND usg.user_id = ?
        WHERE s.topic_id = ?
        """,
        (user_id, topic_id),
    )
    grades = cursor.fetchall()
    conn.close()
    return grades


def get_user_topic_grade(user_id: int, topic_id: int):
    """
    Возвращает суммарную (среднюю) оценку пользователя по теме.
    Подсчёт: среднее арифметическое по всем разделам темы,
    где у пользователя есть оценка.
    Если ни по одному разделу нет оценки — возвращает None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT AVG(usg.grade)
        FROM sections s
        LEFT JOIN user_section_grades usg
        ON s.id = usg.section_id AND usg.user_id = ?
        WHERE s.topic_id = ? AND usg.grade IS NOT NULL
        """,
        (user_id, topic_id),
    )
    avg_grade = cursor.fetchone()[0]
    conn.close()
    return avg_grade


def get_last_lesson_for_user(user_id: int):
    """
    Возвращает последнее занятие пользователя:
    (updated_at, subj_name, topic_name, section_name, grade) или None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT usg.updated_at, s.name, t.name, sec.name, usg.grade
        FROM user_section_grades usg
        JOIN sections sec ON sec.id = usg.section_id
        JOIN topics t ON t.id = sec.topic_id
        JOIN subjects s ON s.id = t.subject_id
        WHERE usg.user_id = ?
        ORDER BY usg.updated_at DESC
        LIMIT 1
    """,
        (user_id,),
    )
    result = cursor.fetchone()
    conn.close()
    return result
