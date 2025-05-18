import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def init_db():
    """
    Инициализация бд: создает файл reminders.db
    и таблицы  reminders и users, если её ещё нет
    """
    # Таблица с напоминаниями
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                remind_time TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
                )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    username TEXT NOT NULL
                )
    """
    )
    conn.commit()
    conn.close()


def add_user(chat_id: int, first_name: str, last_name: str, username: str):
    """
    Добавляет пользователя в БД
    Возвращает True если пользователь добавлен, False если уже есть
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
    Возвращает информацию о пользователе по chat_id
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reminders WHERE chat_id=?", (chat_id,))
    total = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT id, remind_time, message
        FROM reminders WHERE chat_id=?
        ORder by remind_time ASC
        LIMIT 1
        """,
        (chat_id,),
    )
    total_reminders = cursor.fetchone()
    conn.close()
    if total_reminders:
        rem_id, rt_str, msg = total_reminders
        remind_dt = datetime.fromisoformat(rt_str)
        return total, (rem_id, remind_dt, msg)
    else:
        return total, None


def add_reminder(chat_id: int, remind_time: datetime, message: str) -> int:
    """
    Добавляет напоминание в БД
    Возвращает сгенереный ИД напоминания
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
        INSERT INTO reminders(id, chat_id, remind_time, message)
        VALUES (?,?,?,?)
        """,
        (free_id, chat_id, remind_time.isoformat(), message),
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
