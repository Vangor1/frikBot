import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def add_subject(name: str, description: str = None):
    """
    Добавляет новый предмет (subject) в БД.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (name, description) VALUES (?, ?)",
        (name, description),
    )
    conn.commit()
    conn.close()


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


def add_topic(subject_id: int, name: str, description: str = None):
    """
    Добавляет новую тему (topic) в определённый предмет.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO topics (subject_id, name, description) VALUES (?, ?, ?)",
        (subject_id, name, description),
    )
    conn.commit()
    conn.close()


def get_topics_by_subject(subject_id: int):
    """
    Возвращает список тем для заданного предмета: (id, name, description)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description FROM topics WHERE subject_id=?",
        (subject_id,),
    )
    topics = cursor.fetchall()
    conn.close()
    return topics


def add_section(topic_id: int, name: str, description: str = None):
    """
    Добавляет новый раздел (section) в тему.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sections (topic_id, name, description) VALUES (?, ?, ?)",
        (topic_id, name, description),
    )
    conn.commit()
    conn.close()


def get_sections_by_topic(topic_id: int):
    """
    Возвращает список разделов для заданной темы: (id, name, description)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description FROM sections WHERE topic_id=?",
        (topic_id,),
    )
    sections = cursor.fetchall()
    conn.close()
    return sections
