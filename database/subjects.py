import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


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
