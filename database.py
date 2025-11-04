from config import DB_CONFIG
import os
import psycopg2
from typing import Optional, List
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        self.db_config = DB_CONFIG

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**self.db_config)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# Глобальный экземпляр
db = DatabaseManager()


# 🔧 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ КОНВЕРТАЦИИ
def row_to_dict(row, fields):
    """Конвертирует строку в словарь"""
    if not row:
        return None
    return {fields[i]: row[i] for i in range(len(fields))}


def get_user_dict(user_row):
    fields = ['user_id', 'username', 'name', 'location', 'interests', 'created_at']
    return row_to_dict(user_row, fields)


def get_club_dict(club_row):
    fields = ['club_id', 'owner_id', 'name', 'description', 'tags', 'location',
              'chat_link', 'is_active', 'created_at']
    return row_to_dict(club_row, fields)


def get_member_dict(member_row):
    fields = ['user_id', 'club_id', 'joined_at']
    return row_to_dict(member_row, fields)


# 📊 ОСНОВНЫЕ ФУНКЦИИ БАЗЫ ДАННЫХ
def initialize_database():
    """Инициализирует базу данных - создает таблицы если их нет"""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # PostgreSQL таблицы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                name VARCHAR(255) NOT NULL,
                location TEXT,
                interests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clubs (
                club_id SERIAL PRIMARY KEY,
                owner_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                tags TEXT,
                location TEXT,
                chat_link TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                user_id BIGINT,
                club_id INTEGER,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, club_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (club_id) REFERENCES clubs (club_id)
            )
        ''')

        # Индексы
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clubs_tags ON clubs(tags)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clubs_location ON clubs(location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clubs_active ON clubs(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_club ON members(club_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_user ON members(user_id)')

        print("✅ База данных инициализирована в облаке (PostgreSQL)")


def get_user_by_tg_id(tg_id: int):
    """Получить пользователя по Telegram ID"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (tg_id,))
        user = cursor.fetchone()
        return get_user_dict(user)


def create_user(tg_id: int, name: str, username: str = None, location: str = None, interests: str = None) -> bool:
    """Создать нового пользователя"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, username, name, location, interests) VALUES (%s, %s, %s, %s, %s)",
                (tg_id, username, name, location, interests)
            )
            return True
    except Exception as e:
        print(f"Ошибка создания пользователя: {e}")
        return False


def update_user(tg_id: int, name: str = None, location: str = None, interests: str = None) -> bool:
    """Обновить данные пользователя"""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if location is not None:
            updates.append("location = %s")
            params.append(location)
        if interests is not None:
            updates.append("interests = %s")
            params.append(interests)

        if not updates:
            return False

        params.append(tg_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"

        cursor.execute(query, params)
        affected = cursor.rowcount
        return affected > 0


def create_club(owner_id: int, name: str, description: str, tags: str, location: str, chat_link: str) -> int:
    """Создать новый клуб. Возвращает ID созданного клуба"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clubs (owner_id, name, description, tags, location, chat_link) VALUES (%s, %s, %s, %s, %s, %s) RETURNING club_id",
            (owner_id, name, description, tags, location, chat_link)
        )
        club_id = cursor.fetchone()[0]
        return club_id


def get_club_by_id(club_id: int):
    """Получить данные клуба по ID"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clubs WHERE club_id = %s AND is_active = TRUE", (club_id,))
        club = cursor.fetchone()
        return get_club_dict(club)


def get_clubs_by_owner(owner_id: int):
    """Получить все клубы, созданные пользователем"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clubs WHERE owner_id = %s AND is_active = TRUE ORDER BY created_at DESC",
                       (owner_id,))
        clubs = cursor.fetchall()
        return [get_club_dict(club) for club in clubs]


def search_clubs_by_tag(tag: str, limit: int = 10):
    """Найти клубы по тегу"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM clubs WHERE tags LIKE %s AND is_active = TRUE ORDER BY created_at DESC LIMIT %s",
            (f'%{tag}%', limit)
        )
        clubs = cursor.fetchall()
        return [get_club_dict(club) for club in clubs]


def search_clubs_by_location(location: str, limit: int = 10):
    """Найти клубы по локации"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM clubs WHERE location LIKE %s AND is_active = TRUE ORDER BY created_at DESC LIMIT %s",
            (f'%{location}%', limit)
        )
        clubs = cursor.fetchall()
        return [get_club_dict(club) for club in clubs]


def get_all_active_clubs(limit: int = 20):
    """Получить все активные клубы"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clubs WHERE is_active = TRUE ORDER BY created_at DESC LIMIT %s", (limit,))
        clubs = cursor.fetchall()
        return [get_club_dict(club) for club in clubs]


def add_member_to_club(user_id: int, club_id: int) -> bool:
    """Добавить пользователя в клуб как участника"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (user_id, club_id) VALUES (%s, %s)",
                (user_id, club_id)
            )
            return True
    except Exception as e:
        print(f"Ошибка добавления участника: {e}")
        return False


def remove_member_from_club(user_id: int, club_id: int) -> bool:
    """Удалить пользователя из клуба"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE user_id = %s AND club_id = %s", (user_id, club_id))
        affected = cursor.rowcount
        return affected > 0


def get_club_members(club_id: int):
    """Получить всех участников клуба"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.username, u.name, u.location, u.interests, u.created_at
            FROM users u 
            JOIN members m ON u.user_id = m.user_id 
            WHERE m.club_id = %s
        ''', (club_id,))
        members = cursor.fetchall()
        return [get_user_dict(member) for member in members]


def get_user_clubs(user_id: int):
    """Получить все клубы, в которых состоит пользователь"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.* 
            FROM clubs c 
            JOIN members m ON c.club_id = m.club_id 
            WHERE m.user_id = %s AND c.is_active = TRUE
            ORDER BY m.joined_at DESC
        ''', (user_id,))
        clubs = cursor.fetchall()
        return [get_club_dict(club) for club in clubs]


def is_user_club_member(user_id: int, club_id: int) -> bool:
    """Проверить, является ли пользователь участником клуба"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM members WHERE user_id = %s AND club_id = %s", (user_id, club_id))
        result = cursor.fetchone() is not None
        return result


def is_user_club_owner(user_id: int, club_id: int) -> bool:
    """Проверить, является ли пользователь владельцем клуба"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM clubs WHERE club_id = %s AND owner_id = %s", (club_id, user_id))
        result = cursor.fetchone() is not None
        return result


def deactivate_club(club_id: int) -> bool:
    """Деактивировать клуб (мягкое удаление)"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE clubs SET is_active = FALSE WHERE club_id = %s", (club_id,))
        affected = cursor.rowcount
        return affected > 0


def update_club(club_id: int, name: str = None, description: str = None, tags: str = None, location: str = None,
                chat_link: str = None) -> bool:
    """Обновить данные клуба"""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if tags is not None:
            updates.append("tags = %s")
            params.append(tags)
        if location is not None:
            updates.append("location = %s")
            params.append(location)
        if chat_link is not None:
            updates.append("chat_link = %s")
            params.append(chat_link)

        if not updates:
            return False

        params.append(club_id)
        query = f"UPDATE clubs SET {', '.join(updates)} WHERE club_id = %s"

        cursor.execute(query, params)
        affected = cursor.rowcount
        return affected > 0