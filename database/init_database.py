import os
import sqlite3

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
                chat_id INTEGER NOT NULL,           -- Telegram chat_id пользователя, кому адресовано напоминание
                remind_time TEXT NOT NULL,          -- Время напоминания (строка в формате ISO)
                message TEXT NOT NULL,              -- Текст напоминания
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
                )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,    -- Telegram chat_id пользователя
                    first_name TEXT NOT NULL,       -- Имя пользователя
                    last_name TEXT NOT NULL,        -- Фамилия пользователя (может быть пустой строкой)
                    username TEXT NOT NULL          -- Имя пользователя в Telegram (может быть пустой строкой)
                )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,                     -- Название предмета
            description TEXT                        -- Описание предмета (может быть пустым)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            subject_id INTEGER NOT NULL,            -- ID предмета, к которому относится тема
            name TEXT NOT NULL,                     -- Название темы
            description TEXT,                       -- Описание темы (может быть пустым)
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY,
            topic_id INTEGER NOT NULL,              -- ID темы, к которой относится раздел
            name TEXT NOT NULL,                     -- Название раздела
            description TEXT,                       -- Описание раздела (может быть пустым)
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_section_grades (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,               -- ID пользователя, которому принадлежит оценка
            section_id INTEGER NOT NULL,            -- ID раздела, к которому относится оценка
            grade INTEGER NOT NULL,                 -- Оценка пользователя по разделу
            updated_at TEXT NOT NULL,               -- Дата и время последнего обновления оценки (строка в формате ISO)
            FOREIGN KEY(user_id) REFERENCES users(chat_id),
            FOREIGN KEY(section_id) REFERENCES sections(id)
        )
        """
    )
    conn.commit()
    conn.close()
