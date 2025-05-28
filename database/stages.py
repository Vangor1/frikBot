import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def get_stages_by_subject(subject_id: int):
    """
    Возвращает список всех этапов для заданного предмета: (id, name, description)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description FROM stages WHERE subject_id = ?", (subject_id,)
    )
    stages = cursor.fetchall()
    conn.close()
    return stages
