import sqlite3

from .db import DB_PATH


def get_topics_by_section(section_id: int):
    """
    Возвращает все разделы для данного этапа.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM topics WHERE section_id = ?", (section_id,))
    sections = cursor.fetchall()
    conn.close()
    return sections
