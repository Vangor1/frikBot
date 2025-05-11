import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def init_db():
    """
    Инициализация бд: создает файл reminders.db
    и таблицу  reminders, если её ещё нет
    """
    # Таблица с напоминаниями
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS reminders (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   chat_id INTEGER NOT NULL,
                   remind_time TEXT NOT NULL,
                   message TEXT NOT NULL
                   )
    """
    )
    conn.commit()
    conn.close()


def add_reminder(chat_id: int, remind_time: datetime, message: str) -> int:
    """
    Добавляет напоминание в БД
    Возвращает сгенереный ИД напоминания
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO reminders(
                   chat_id, remind_time, message)
                   VALUES (?,?,?)""",
        (chat_id, remind_time.isoformat(), message),
    )
    reminder_id = cursor.lastrowid  # id для удаления
    conn.commit()
    conn.close()
    return reminder_id


def get_pending_reminders():
    """
    Возвращает список всех напоминаний в формате:
    (id, chat_id, remind_datetime, message)
    используется при старте бота для того чтобы восстановить задачи
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
    Удаляет напоминание с указанным ИД из базы
    Вызывается при успешном выполнении или при отмене пользователем
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def get_reminders_by_chat(chat_id: int):
    """
    Возвращает все напоминания принадлежащие конкретному чату
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
    Возвращает запись по id или None если записи нет
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
