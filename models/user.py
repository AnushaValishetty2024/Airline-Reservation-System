import re
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config


def get_db_connection():
    """Create and return a MySQL database connection."""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset=Config.MYSQL_CHARSET,
    )


def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(pattern, email or ""))


def is_valid_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r"^[0-9+().-]{7,15}$", mobile or ""))


def is_strong_password(password: str) -> bool:
    return len(password or "") >= 8 and any(ch.isupper() for ch in password or "") and any(ch.isdigit() for ch in password or "")


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def get_role_by_name(role_name: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, role_name FROM user_roles WHERE role_name = %s", (role_name,))
    role = cursor.fetchone()
    cursor.close()
    conn.close()
    return role


def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT u.id, u.full_name, u.email, u.mobile_number, u.password_hash, u.role_id, r.role_name "
        "FROM users u JOIN user_roles r ON u.role_id = r.id WHERE u.email = %s",
        (email,),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT u.id, u.full_name, u.email, u.mobile_number, u.password_hash, u.role_id, r.role_name "
        "FROM users u JOIN user_roles r ON u.role_id = r.id WHERE u.id = %s",
        (user_id,),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def create_user(full_name: str, email: str, mobile_number: str, password: str) -> int:
    role = get_role_by_name("User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email, mobile_number, password_hash, role_id) VALUES (%s, %s, %s, %s, %s)",
        (full_name, email, mobile_number, hash_password(password), role["id"]),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def update_user_profile(user_id: int, full_name: str, email: str, mobile_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET full_name = %s, email = %s, mobile_number = %s WHERE id = %s",
        (full_name, email, mobile_number, user_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_password(user_id: int, new_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hash_password(new_password), user_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT u.id, u.full_name, u.email, u.mobile_number, u.is_active, r.role_name FROM users u "
        "JOIN user_roles r ON u.role_id = r.id ORDER BY u.id"
    )
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users
