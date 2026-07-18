from models.db import get_db_connection


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


def create_user(full_name: str, email: str, mobile_number: str, password_hash: str, role_id: int) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email, mobile_number, password_hash, role_id) VALUES (%s, %s, %s, %s, %s)",
        (full_name, email, mobile_number, password_hash, role_id),
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


def update_password(user_id: int, password_hash: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
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


def toggle_user_status(user_id: int):
    """Toggle user active/inactive status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = NOT is_active WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.rowcount > 0
