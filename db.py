import sqlite3
from datetime import datetime

DB_PATH = 'reminders.db'

def init_db():
    """
    Инициализация бд: создает файл reminders.db
    и таблицу  reminders, если её ещё нет
    """
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   chat_id INTEGER NOT NULL,
                   remind_time TEXT NOT NULL,
                   message TEXT NOT NULL
                   )
    """)
    conn.commit()
    conn.close()

def add_reminder(chat_id: int, remind_time:datetime, message:str)->int:
    """
    Добавляет напоминание в БД
    Возвращает сгенереный ИД напоминания
    """
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute("""
    INSERT INTO reminders(
                   chat_id, remind_rime, message)
                   VALUES (?,?,?)""", (chat_id, remind_time.isoformat(), message)
                   )
    reminder_id =cursor.lastrowid
    conn.commit()
    conn.close()
    return reminder_id

def get_pending_reminders():
    """
    Возвращает список всех напоминаний в формате:
    (id, chat_id, remind_datetime, message)    
    """
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute('SELECT id, chat_id, remind_time, message FROM reminders')
    rows=cursor.fetchall()
    conn.close()
    return [
        (row[0], row[1], datetime.fromisoformat(row[2]), row[3])
        for row in rows
    ]
def delete_reminder (reminder_id:int):
    """
    Удаляет напоминание с указанным ИД из базы
    """
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
