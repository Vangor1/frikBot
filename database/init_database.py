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
    # Таблица напоминаний
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
    # Таблица пользователей
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
    # Таблица предметов
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,                  -- Название предмета
            description TEXT                     -- Описание предмета
        )
        """
    )
    # Таблица этапов/уровней
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stages (
            id INTEGER PRIMARY KEY,
            subject_id INTEGER NOT NULL,         -- ID предмета, которому принадлежит этап
            name TEXT NOT NULL,                  -- Название этапа
            description TEXT,                    -- Описание этапа
            FOREIGN KEY(subject_id) REFERENCES subjects(id) -- Внешний ключ на subjects
        )
        """
    )
    # Таблица разделов внутри этапа
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY,
            stage_id INTEGER NOT NULL,           -- ID этапа, которому принадлежит раздел
            name TEXT NOT NULL,                  -- Название раздела
            description TEXT,                    -- Описание раздела
            FOREIGN KEY(stage_id) REFERENCES stages(id) -- Внешний ключ на stages
        )
        """
    )
    # Таблица тем внутри раздела
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            section_id INTEGER NOT NULL,         -- ID раздела, которому принадлежит тема
            name TEXT NOT NULL,                  -- Название темы
            description TEXT,                    -- Описание темы (например, "Правила чтения и произношения слов")
            FOREIGN KEY(section_id) REFERENCES sections(id) -- Внешний ключ на sections
        )
        """
    )
    # Таблица оценок пользователя по разделам
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_topic_grades (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,            -- ID пользователя (chat_id из users)
            topic_id INTEGER NOT NULL,           -- ID темы
            grade INTEGER NOT NULL,              -- Оценка пользователя по теме
            updated_at TEXT NOT NULL,            -- Дата и время последнего обновления оценки (ISO строка)
            FOREIGN KEY(user_id) REFERENCES users(chat_id), -- Внешний ключ на пользователей
            FOREIGN KEY(topic_id) REFERENCES topics(id)     -- Внешний ключ на темы
        )
        """
    )
    conn.commit()
    conn.close()
