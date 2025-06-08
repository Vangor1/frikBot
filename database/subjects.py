import sqlite3

from .db import DB_PATH


def get_subjects():
    """
    Возвращает список всех предметов: (id, name, description)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    return subjects
