import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


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
