from models.db import get_db_connection


def get_all_schedules(status=None, page=1, per_page=10):
    """Get all flight schedules with optional status filter and pagination."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    offset = (page - 1) * per_page
    query = (
        "SELECT s.schedule_id, s.flight_id, f.flight_number, a.airline_name, "
        "s.departure_time, s.arrival_time, s.price, s.terminal, s.gate_number, s.status, s.created_at "
        "FROM flight_schedule s "
        "INNER JOIN flights f ON s.flight_id = f.id "
        "INNER JOIN airlines a ON f.airline_id = a.id"
    )
    params = []

    if status:
        query += " WHERE s.status = %s"
        params.append(status)

    query += " ORDER BY s.departure_time DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, tuple(params))
    schedules = cursor.fetchall()
    cursor.close()
    conn.close()
    return schedules


def count_schedules(status=None):
    """Count total schedules with optional status filter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM flight_schedule"
    params = []
    if status:
        query += " WHERE status = %s"
        params.append(status)
    cursor.execute(query, tuple(params))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def get_schedule_by_id(schedule_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT schedule_id, flight_id, departure_time, arrival_time, price, terminal, gate_number, status FROM flight_schedule WHERE schedule_id = %s",
        (schedule_id,),
    )
    schedule = cursor.fetchone()
    cursor.close()
    conn.close()
    return schedule


def get_schedules_by_flight(flight_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT schedule_id, departure_time, arrival_time, price, terminal, gate_number, status FROM flight_schedule WHERE flight_id = %s ORDER BY departure_time",
        (flight_id,),
    )
    schedules = cursor.fetchall()
    cursor.close()
    conn.close()
    return schedules


def create_schedule(flight_id: int, departure_time: str, arrival_time: str, price: float, terminal: str = None, gate_number: str = None, status: str = "Scheduled"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO flight_schedule (flight_id, departure_time, arrival_time, price, terminal, gate_number, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (flight_id, departure_time, arrival_time, price, terminal, gate_number, status),
    )
    conn.commit()
    schedule_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return schedule_id


def update_schedule(schedule_id: int, flight_id: int, departure_time: str, arrival_time: str, price: float, terminal: str = None, gate_number: str = None, status: str = "Scheduled"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE flight_schedule SET flight_id = %s, departure_time = %s, arrival_time = %s, price = %s, terminal = %s, gate_number = %s, status = %s WHERE schedule_id = %s",
        (flight_id, departure_time, arrival_time, price, terminal, gate_number, status, schedule_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_schedule(schedule_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flight_schedule WHERE schedule_id = %s", (schedule_id,))
    conn.commit()
    cursor.close()
    conn.close()