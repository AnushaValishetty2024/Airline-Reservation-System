from mysql.connector import Error

from models.user import get_db_connection


def get_all_airlines(status=None, page=1, per_page=10):
    """Get all airlines with optional status filter and pagination."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    offset = (page - 1) * per_page

    query = """
        SELECT
            id,
            airline_name,
            airline_code,
            country,
            founded_year,
            is_active,
            created_at
        FROM airlines
    """

    params = []

    if status is not None:
        query += " WHERE is_active = %s"
        params.append(1 if status == "Active" else 0)

    query += " ORDER BY airline_name LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, tuple(params))
    airlines = cursor.fetchall()

    cursor.close()
    conn.close()

    return airlines


def count_airlines(status=None):
    """Count total airlines with optional status filter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM airlines"
    params = []
    if status:
        query += " WHERE is_active = %s"
        params.append(1 if status == "Active" else 0)
    cursor.execute(query, tuple(params))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def get_airline_by_id(airline_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, airline_name, airline_code, country, is_active FROM airlines WHERE id = %s",
        (airline_id,),
    )
    airline = cursor.fetchone()
    cursor.close()
    conn.close()
    return airline


def get_airline_by_code(airline_code: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM airlines WHERE airline_code = %s",
        (airline_code,),
    )
    airline = cursor.fetchone()
    cursor.close()
    conn.close()
    return airline


def create_airline(airline_name: str, airline_code: str, country: str, status: str = "Active"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO airlines
        (airline_name, airline_code, country, is_active)
        VALUES (%s, %s, %s, %s)
        """,
        (airline_name, airline_code, country, 1 if status == "Active" else 0),
    )
    conn.commit()
    airline_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return airline_id


def update_airline(airline_id: int, airline_name: str, airline_code: str, country: str, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE airlines SET airline_name = %s, airline_code = %s, country = %s, is_active = %s WHERE id = %s",
        (airline_name, airline_code, country, 1 if status == "Active" else 0, airline_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_airline(airline_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM airlines WHERE id = %s", (airline_id,))
    conn.commit()
    cursor.close()
    conn.close()