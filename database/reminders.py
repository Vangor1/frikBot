import sqlite3
from datetime import datetime

from .db import DB_PATH


def add_reminder(
    chat_id: int,
    remind_time: datetime,
    message: str,
    subject_id=None,
    stage_id=None,
    section_id=None,
    topic_id=None,
) -> int:
    """
    Добавляет напоминание для пользователя, возвращает id напоминания.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM reminders ORDER BY id")
    user_ids = [row[0] for row in cursor.fetchall()]
    free_id = 1
    for uid in user_ids:
        if uid != free_id:
            break
        free_id += 1
    cursor.execute(
        """
        INSERT INTO reminders(id, chat_id, remind_time, message,
        subject_id, stage_id, section_id, topic_id)
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            free_id,
            chat_id,
            remind_time.isoformat(),
            message,
            subject_id,
            stage_id,
            section_id,
            topic_id,
        ),
    )
    reminder_id = cursor.lastrowid  # id для удаления
    conn.commit()
    conn.close()
    return reminder_id


def get_pending_reminders():
    """
    Возвращает список всех напоминаний:
    (id, chat_id, дата/время, текст).
    Используется для восстановления задач при запуске бота.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, chat_id, remind_time, message FROM reminders")
    rows = cursor.fetchall()
    conn.close()
    # Преобразование remind_time из строки ISO в datetime
    return [(row[0], row[1], datetime.fromisoformat(row[2]), row[3]) for row in rows]


def delete_reminder(reminder_id: int):
    """
    Удаляет напоминание по его id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def get_reminders_by_chat(chat_id: int):
    """
    Возвращает список всех напоминаний для пользователя.
    Каждый элемент — (id, chat_id, дата/время, текст).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, remind_time, message FROM reminders WHERE chat_id=?",
        (chat_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1], datetime.fromisoformat(row[2]), row[3]) for row in rows]


def get_reminder_by_id(reminder_id: int):
    """
    Возвращает напоминание по его id, если есть, иначе None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, remind_time, message FROM reminders WHERE id=?",
        (reminder_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    rem_id, chat_id, rt_str, message = row
    remind_dt = datetime.fromisoformat(rt_str)
    return (rem_id, chat_id, remind_dt, message)


def get_reminder_details(reminder_id: int):
    """
    Возвращает напоминание вместе с названиями темы и раздела.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.id, r.chat_id, r.remind_time, r.message,
               r.subject_id, r.stage_id, r.section_id, r.topic_id,
               s.name, st.name, sec.name, t.name
        FROM reminders r
        LEFT JOIN subjects s ON r.subject_id = s.id
        LEFT JOIN stages st ON r.stage_id = st.id
        LEFT JOIN sections sec ON r.section_id = sec.id
        LEFT JOIN topics t ON r.topic_id = t.id
        WHERE r.id=?
        """,
        (reminder_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    rt = datetime.fromisoformat(row[2])
    return {
        "id": row[0],
        "chat_id": row[1],
        "remind_time": rt,
        "message": row[3],
        "subject_id": row[4],
        "stage_id": row[5],
        "section_id": row[6],
        "topic_id": row[7],
        "subject_name": row[8],
        "stage_name": row[9],
        "section_name": row[10],
        "topic_name": row[11],
    }
