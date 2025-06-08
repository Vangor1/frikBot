import sqlite3

from .db import DB_PATH


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
