import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def add_user(chat_id: int, first_name: str, last_name: str, username: str):
    """
    Добавляет нового пользователя в таблицу users.
    Если пользователь уже существует — ничего не делает.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO users(chat_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
        """,
        (chat_id, first_name, last_name, username),
    )
    conn.commit()
    conn.close()


def get_user_stats(chat_id: int):
    """
    Возвращает кортеж:
    - количество напоминаний пользователя,
    - (id, дата/время, текст, subject_name, stage_name, section_name, topic_name)
    ближайшего напоминания, если есть.

    subject_name, stage_name, section_name, topic_name - могут быть None, если не
    указаны в напоминании.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reminders WHERE chat_id=?", (chat_id,))
    total = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT r.id, r.remind_time, r.message,
               s.name as subject_name,
               st.name as stage_name,
               sec.name as section_name,
               t.name as topic_name
        FROM reminders r
        LEFT JOIN subjects s ON r.subject_id = s.id
        LEFT JOIN stages st ON r.stage_id = st.id
        LEFT JOIN sections sec ON r.section_id = sec.id
        LEFT JOIN topics t ON r.topic_id = t.id
        WHERE r.chat_id=?
        ORDER BY r.remind_time ASC
        LIMIT 1
        """,
        (chat_id,),
    )
    total_reminders = cursor.fetchone()
    conn.close()
    if total_reminders:
        rem_id, rt_str, msg, subject, stage, section, topic = total_reminders
        remind_dt = datetime.fromisoformat(rt_str)
        return total, (rem_id, remind_dt, msg, subject, stage, section, topic)
    else:
        return total, None


def add_user_subject(user_id: int, subject_id: int):
    """
    Добавляет выбранный предмет для пользователя.
    Если такая пара уже есть, ничего не делает (INSERT OR IGNORE).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO user_subjects (user_id, subject_id) VALUES (?, ?)",
        (user_id, subject_id),
    )
    conn.commit()
    conn.close()


def get_user_subjects(user_id: int):
    """
    Возвращает список предметов, выбранных пользователем.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT subjects.id, subjects.name
        FROM subjects
        INNER JOIN user_subjects ON subjects.id = user_subjects.subject_id
        WHERE user_subjects.user_id = ?
        """,
        (user_id,),
    )
    result = cursor.fetchall()
    conn.close()
    return result


def remove_user_subject(user_id: int, subject_id: int):
    """
    Удаляет выбранный предмет пользователя.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_subjects WHERE user_id = ? AND subject_id = ?",
        (user_id, subject_id),
    )
    conn.commit()
    conn.close()
