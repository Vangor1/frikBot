import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def sync_study_structure(structure):
    """
    Синхронизирует структуру обучения с БД:
    - Добавляет новые предметы, темы, разделы
    - Обновляет имена и описания если изменились
    - Не удаляет существующее (для сохранения прогресса пользователей)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for subj in structure:
        # 1. Предмет (subject)
        cursor.execute("SELECT id FROM subjects WHERE name=?", (subj["name"],))
        subj_row = cursor.fetchone()
        if subj_row:
            subject_id = subj_row[0]
            cursor.execute(
                "UPDATE subjects SET description=? WHERE id=?",
                (subj.get("description", ""), subject_id),
            )
        else:
            cursor.execute(
                "INSERT INTO subjects (name, description) VALUES (?, ?)",
                (subj["name"], subj.get("description", "")),
            )
            subject_id = cursor.lastrowid

        # 2. Темы (topics)
        for topic in subj["topics"]:
            cursor.execute(
                "SELECT id FROM topics WHERE name=? AND subject_id=?",
                (topic["name"], subject_id),
            )
            topic_row = cursor.fetchone()
            if topic_row:
                topic_id = topic_row[0]
                cursor.execute(
                    "UPDATE topics SET description=? WHERE id=?",
                    (topic.get("description", ""), topic_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO topics (subject_id, name, description) VALUES (?, ?, ?)
                    """,
                    (subject_id, topic["name"], topic.get("description", "")),
                )
                topic_id = cursor.lastrowid

            # 3. Разделы (sections)
            for section in topic["sections"]:
                cursor.execute(
                    "SELECT id FROM sections WHERE name=? AND topic_id=?",
                    (section["name"], topic_id),
                )
                section_row = cursor.fetchone()
                if section_row:
                    section_id = section_row[0]
                    cursor.execute(
                        "UPDATE sections SET description=? WHERE id=?",
                        (section.get("description", ""), section_id),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO sections (topic_id, name, description)
                        VALUES (?, ?, ?)
                        """,
                        (topic_id, section["name"], section.get("description", "")),
                    )
    conn.commit()
    conn.close()
