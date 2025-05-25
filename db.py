import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "reminders.db")


def init_db():
    """
    Инициализация бд: создает файл reminders.db
    и все нужные таблицы:
    - users: пользователи Telegram
    - reminders: напоминания пользователя
    - subjects: предметы обучения
    - topics: темы в рамках предмета
    - sections: разделы в рамках темы
    - user_section_grades: оценки пользователя по разделам
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                remind_time TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
                )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    username TEXT NOT NULL
                )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY,
            topic_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_section_grades (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            grade INTEGER NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(chat_id),
            FOREIGN KEY(section_id) REFERENCES sections(id)
        )
        """
    )
    conn.commit()
    conn.close()


def add_user(chat_id: int, first_name: str, last_name: str, username: str):
    """
    Добавляет нового пользователя в таблицу users.
    Если пользователь уже существует — ничего не делает.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO users(chat_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
        """,
        (chat_id, first_name, last_name, username),
    )
    conn.commit()
    conn.close()


def get_user_stats(chat_id: int):
    """
    Возвращает кортеж:
    - количество напоминаний пользователя,
    - (id, дата/время, текст) ближайшего напоминания, если есть.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reminders WHERE chat_id=?", (chat_id,))
    total = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT id, remind_time, message
        FROM reminders WHERE chat_id=?
        ORder by remind_time ASC
        LIMIT 1
        """,
        (chat_id,),
    )
    total_reminders = cursor.fetchone()
    conn.close()
    if total_reminders:
        rem_id, rt_str, msg = total_reminders
        remind_dt = datetime.fromisoformat(rt_str)
        return total, (rem_id, remind_dt, msg)
    else:
        return total, None


def add_reminder(chat_id: int, remind_time: datetime, message: str) -> int:
    """
    Добавляет напоминание для пользователя, возвращает id напоминания.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM reminders ORDER BY id")
    user_ids = [row[0] for row in cursor.fetchall()]
    free_id = 1
    for uid in user_ids:
        if uid != free_id:
            break
        free_id += 1
    cursor.execute(
        """
        INSERT INTO reminders(id, chat_id, remind_time, message)
        VALUES (?,?,?,?)
        """,
        (free_id, chat_id, remind_time.isoformat(), message),
    )
    reminder_id = cursor.lastrowid  # id для удаления
    conn.commit()
    conn.close()
    return reminder_id


def get_pending_reminders():
    """
    Возвращает список всех напоминаний:
    (id, chat_id, дата/время, текст).
    Используется для восстановления задач при запуске бота.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, chat_id, remind_time, message FROM reminders")
    rows = cursor.fetchall()
    conn.close()
    # Преобразование remind_time из строки ISO в datetime
    return [(row[0], row[1], datetime.fromisoformat(row[2]), row[3]) for row in rows]


def delete_reminder(reminder_id: int):
    """
    Удаляет напоминание по его id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def get_reminders_by_chat(chat_id: int):
    """
    Возвращает список всех напоминаний для пользователя.
    Каждый элемент — (id, chat_id, дата/время, текст).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, remind_time, message FROM reminders WHERE chat_id=?",
        (chat_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1], datetime.fromisoformat(row[2]), row[3]) for row in rows]


def get_reminder_by_id(reminder_id: int):
    """
    Возвращает напоминание по его id, если есть, иначе None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, remind_time, message FROM reminders WHERE id=?",
        (reminder_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    rem_id, chat_id, rt_str, message = row
    remind_dt = datetime.fromisoformat(rt_str)
    return (rem_id, chat_id, remind_dt, message)


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


def set_user_section_grade(user_id: int, section_id: int, grade: int):
    """
    Ставит или обновляет оценку пользователя за конкретный раздел.
    Если оценка уже есть — обновляет; если нет — добавляет.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "SELECT id FROM user_section_grades WHERE user_id=? AND section_id=?",
        (user_id, section_id),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            """
            UPDATE user_section_grades
            SET grade=?, updated_at=?
            WHERE user_id=? AND section_id=?
            """,
            (grade, now, user_id, section_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO user_section_grades (user_id, section_id, grade, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, section_id, grade, now),
        )
    conn.commit()
    conn.close()


def get_user_section_grade(user_id: int, section_id: int):
    """
    Возвращает (grade, updated_at) — оценку пользователя по разделу и дату обновления.
    Если оценки нет — возвращает None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT grade, updated_at
        FROM user_section_grades
        WHERE user_id=? AND section_id=?
        """,
        (user_id, section_id),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def get_user_grades_by_topic(user_id: int, topic_id: int):
    """
    Возвращает список оценок пользователя по всем разделам темы:
    (section_id, section_name, grade, updated_at)
    Если по какому-то разделу нет оценки — grade будет None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.id, s.name, usg.grade, usg.updated_at
        FROM sections s
        LEFT JOIN user_section_grades usg
        ON s.id = usg.section_id AND usg.user_id = ?
        WHERE s.topic_id = ?
        """,
        (user_id, topic_id),
    )
    grades = cursor.fetchall()
    conn.close()
    return grades


def get_user_topic_grade(user_id: int, topic_id: int):
    """
    Возвращает суммарную (среднюю) оценку пользователя по теме.
    Подсчёт: среднее арифметическое по всем разделам темы,
    где у пользователя есть оценка.
    Если ни по одному разделу нет оценки — возвращает None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT AVG(usg.grade)
        FROM sections s
        LEFT JOIN user_section_grades usg
        ON s.id = usg.section_id AND usg.user_id = ?
        WHERE s.topic_id = ? AND usg.grade IS NOT NULL
        """,
        (user_id, topic_id),
    )
    avg_grade = cursor.fetchone()[0]
    conn.close()
    return avg_grade


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
