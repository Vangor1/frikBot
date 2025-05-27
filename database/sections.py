import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def get_next_section(current_section_id: int):
    """
    Возвращает id следующего раздела внутри того же этапа.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Получаем stage_id текущего раздела
    cursor.execute("SELECT stage_id FROM sections WHERE id = ?", (current_section_id,))
    stage_id = cursor.fetchone()
    if not stage_id:
        conn.close()
        return None
    stage_id = stage_id[0]
    # Получаем все разделы этапа по возрастанию id
    cursor.execute(
        "SELECT id FROM sections WHERE stage_id = ? ORDER BY id ASC", (stage_id,)
    )
    sections = [row[0] for row in cursor.fetchall()]
    conn.close()
    if current_section_id in sections:
        current_index = sections.index(current_section_id)
        if current_index + 1 < len(sections):
            return sections[current_index + 1]
    return None  # Если нет следующего раздела, возвращаем None
