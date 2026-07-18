from models.db import get_db_connection


def get_all_routes(status=None, page=1, per_page=10):
    """Get all routes with optional status filter and pagination."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    offset = (page - 1) * per_page
    query = "SELECT route_id, source_airport, destination_airport, distance_km, duration_minutes, status, created_at FROM routes"
    params = []

    if status:
        query += " WHERE status = %s"
        params.append(status)

    query += " ORDER BY source_airport, destination_airport LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, tuple(params))
    routes = cursor.fetchall()
    cursor.close()
    conn.close()
    return routes


def count_routes(status=None):
    """Count total routes with optional status filter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM routes"
    params = []
    if status:
        query += " WHERE status = %s"
        params.append(status)
    cursor.execute(query, tuple(params))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def get_route_by_id(route_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT route_id, source_airport, destination_airport, distance_km, duration_minutes, status FROM routes WHERE route_id = %s",
        (route_id,),
    )
    route = cursor.fetchone()
    cursor.close()
    conn.close()
    return route


def create_route(source_airport: str, destination_airport: str, distance_km: float, duration_minutes: int, status: str = "Active"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO routes (source_airport, destination_airport, distance_km, duration_minutes, status) VALUES (%s, %s, %s, %s, %s)",
        (source_airport, destination_airport, distance_km, duration_minutes, status),
    )
    conn.commit()
    route_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return route_id


def update_route(route_id: int, source_airport: str, destination_airport: str, distance_km: float, duration_minutes: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE routes SET source_airport = %s, destination_airport = %s, distance_km = %s, duration_minutes = %s, status = %s WHERE route_id = %s",
        (source_airport, destination_airport, distance_km, duration_minutes, status, route_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_route(route_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routes WHERE route_id = %s", (route_id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_route_by_source_destination(source_airport: str, destination_airport: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT route_id FROM routes WHERE source_airport = %s AND destination_airport = %s",
        (source_airport, destination_airport),
    )
    route = cursor.fetchone()
    cursor.close()
    conn.close()
    return route