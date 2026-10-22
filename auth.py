"""Вход пользователей и хранение паролей для проекта."""
import hashlib
import hmac
import os
import sqlite3
from core_database import connect

ITERATIONS = 260_000


def hash_password(password):
    """PBKDF2-HMAC-SHA256 с индивидуальной случайной солью."""
    if not isinstance(password, str) or len(password) < 6:
        raise ValueError('Пароль должен содержать не менее 6 символов')
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return f'pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}'


def verify_password(password, stored):
    try:
        algorithm, count, salt_hex, digest_hex = stored.split('$')
        if algorithm != 'pbkdf2_sha256':
            return False
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                    bytes.fromhex(salt_hex), int(count))
        return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
    except (ValueError, TypeError, AttributeError):
        return False


def ensure_admin(db_path=None):
    """Первый запуск: создаёт учебную учётную запись администратора."""
    with connect(db_path) as conn:
        if conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
            conn.execute('INSERT INTO users(username,password_hash,role) VALUES(?,?,?)',
                         ('admin', hash_password('admin123'), 'admin'))


def login(username, password, db_path=None):
    with connect(db_path) as conn:
        row = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if row is None or not verify_password(password, row['password_hash']):
        return None
    result = dict(row)
    result.pop('password_hash', None)
    return result


def register_user(username, password, linked_id=None, db_path=None):
    """Регистрация с ограниченной ролью user; admin здесь назначить нельзя."""
    username = username.strip()
    if not username or len(username) > 50:
        raise ValueError('Некорректный логин')
    hashed = hash_password(password)
    with connect(db_path) as conn:
        cursor = conn.execute(
            'INSERT INTO users(username,password_hash,role,client_id) VALUES(?,?,?,?)',
            (username, hashed, 'user', linked_id))
        return cursor.lastrowid


def register_client(username, password, client_id, db_path=None):
    return register_user(username, password, client_id, db_path)
