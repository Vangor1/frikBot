import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def sync_study_structure(structure):
    """
    Синхронизирует структуру обучения с БД по иерархии:
    предмет → этап → раздел → тема
    - Добавляет новые элементы
    - Обновляет имена и описания, если изменились
    - Не удаляет существующие элементы
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    subject = structure

    # Синхронизация предмета
    cursor.execute("SELECT id FROM subjects WHERE name=?", (subject["name"],))
    subj_row = cursor.fetchone()
    if subj_row:
        subject_id = subj_row[0]
        cursor.execute(
            "UPDATE subjects SET description=? WHERE id=?",
            (subject.get("description", ""), subject_id),
        )
    else:
        cursor.execute(
            "INSERT INTO subjects (name, description) VALUES (?, ?)",
            (subject["name"], subject.get("description", "")),
        )
        subject_id = cursor.lastrowid

    # Этапы
    for stage in subject["stages"]:
        cursor.execute(
            "SELECT id FROM stages WHERE name=? AND subject_id=?",
            (stage["name"], subject_id),
        )
        stage_row = cursor.fetchone()
        if stage_row:
            stage_id = stage_row[0]
            cursor.execute(
                "UPDATE stages SET description=? WHERE id=?",
                (stage.get("description", ""), stage_id),
            )
        else:
            cursor.execute(
                "INSERT INTO stages (subject_id, name, description) VALUES (?, ?, ?)",
                (subject_id, stage["name"], stage.get("description", "")),
            )
            stage_id = cursor.lastrowid

        # Разделы
        for section in stage["sections"]:
            cursor.execute(
                "SELECT id FROM sections WHERE name=? AND stage_id=?",
                (section["name"], stage_id),
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
                    """INSERT INTO sections (stage_id, name, description)
                    VALUES (?, ?, ?)""",
                    (stage_id, section["name"], section.get("description", "")),
                )
                section_id = cursor.lastrowid

            # Темы
            for topic_name in section["topics"]:
                cursor.execute(
                    "SELECT id FROM topics WHERE name=? AND section_id=?",
                    (topic_name, section_id),
                )
                topic_row = cursor.fetchone()
                if topic_row:
                    cursor.execute(
                        "UPDATE topics SET description=? WHERE id=?",
                        ("", topic_row[0]),
                    )
                else:
                    cursor.execute(
                        """INSERT INTO topics (section_id, name, description)
                        VALUES (?, ?, ?)""",
                        (section_id, topic_name, ""),
                    )

    conn.commit()
    conn.close()
