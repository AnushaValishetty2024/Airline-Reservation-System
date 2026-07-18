from models.db import get_db_connection


def get_booking_by_id(booking_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT b.id, b.booking_reference, b.user_id, b.flight_id, b.booking_status_id,
               b.total_amount, b.booked_at,
               bs.status_name AS booking_status,
               f.flight_number, f.departure_datetime, f.arrival_datetime,
               a.airline_name, o.airport_code AS origin_code, o.city AS origin_city,
               d.airport_code AS destination_code, d.city AS destination_city,
               ac.aircraft_model
        FROM bookings b
        JOIN booking_status bs ON b.booking_status_id = bs.id
        JOIN flights f ON b.flight_id = f.id
        JOIN airlines a ON f.airline_id = a.id
        JOIN airports o ON f.origin_airport_id = o.id
        JOIN airports d ON f.destination_airport_id = d.id
        JOIN aircraft ac ON f.aircraft_id = ac.id
        WHERE b.id = %s
        """,
        (booking_id,),
    )
    booking = cursor.fetchone()
    cursor.close()
    conn.close()
    return booking


def get_user_bookings(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT b.id, b.booking_reference, b.flight_id, b.booking_status_id,
               b.total_amount, b.booked_at,
               bs.status_name AS booking_status,
               f.flight_number, f.departure_datetime, f.arrival_datetime,
               a.airline_name, o.airport_code AS origin_code, d.airport_code AS destination_code,
               ac.aircraft_model
        FROM bookings b
        JOIN booking_status bs ON b.booking_status_id = bs.id
        JOIN flights f ON b.flight_id = f.id
        JOIN airlines a ON f.airline_id = a.id
        JOIN airports o ON f.origin_airport_id = o.id
        JOIN airports d ON f.destination_airport_id = d.id
        JOIN aircraft ac ON f.aircraft_id = ac.id
        WHERE b.user_id = %s
        ORDER BY b.booked_at DESC
        """,
        (user_id,),
    )
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return bookings


def get_status_id_by_name(status_table: str, status_name: str):
    """Get ID from status table by name."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    table_map = {
        "booking": "booking_status",
        "payment": "payment_status",
        "ticket": "ticket_status",
    }
    table = table_map.get(status_table, status_table)
    cursor.execute(f"SELECT id FROM {table} WHERE status_name = %s", (status_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["id"] if result else None


def get_flight_seats(flight_id: int):
    """Get available seats for a flight."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT seats_economy, seats_business FROM flights WHERE id = %s",
        (flight_id,),
    )
    flight = cursor.fetchone()
    cursor.close()
    conn.close()
    return flight


def create_booking(conn, cursor, user_id, flight_id, booking_reference, booking_status_id, total_amount):
    """Create a booking within an existing transaction."""
    cursor.execute(
        "INSERT INTO bookings (booking_reference, user_id, flight_id, booking_status_id, total_amount) "
        "VALUES (%s, %s, %s, %s, %s)",
        (booking_reference, user_id, flight_id, booking_status_id, total_amount),
    )
    return cursor.lastrowid


def create_passenger(conn, cursor, full_name, email, mobile_number, passport_number):
    """Create a passenger within an existing transaction."""
    cursor.execute(
        "INSERT INTO passengers (full_name, email, mobile_number, passport_number) "
        "VALUES (%s, %s, %s, %s)",
        (full_name, email, mobile_number, passport_number),
    )
    return cursor.lastrowid


def create_booking_passenger(conn, cursor, booking_id, passenger_id, ticket_status_id, seat_number):
    """Create booking_passenger link within an existing transaction."""
    cursor.execute(
        "INSERT INTO booking_passengers (booking_id, passenger_id, ticket_status_id, seat_number) "
        "VALUES (%s, %s, %s, %s)",
        (booking_id, passenger_id, ticket_status_id, seat_number),
    )


def create_payment(conn, cursor, booking_id, payment_reference, amount, payment_method, payment_status_id):
    """Create a payment record within an existing transaction."""
    cursor.execute(
        "INSERT INTO payments (booking_id, payment_reference, amount, payment_method, payment_status_id) "
        "VALUES (%s, %s, %s, %s, %s)",
        (booking_id, payment_reference, amount, payment_method, payment_status_id),
    )


def update_flight_seats(conn, cursor, flight_id: int, seat_class: str, count: int):
    """Update flight seat counts within an existing transaction."""
    if seat_class.lower() == "economy":
        cursor.execute(
            "UPDATE flights SET seats_economy = seats_economy - %s WHERE id = %s",
            (count, flight_id),
        )
    elif seat_class.lower() == "business":
        cursor.execute(
            "UPDATE flights SET seats_business = seats_business - %s WHERE id = %s",
            (count, flight_id),
        )


def get_booking_passengers(booking_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.full_name, p.email, p.mobile_number, p.passport_number,
                   p.gender, p.date_of_birth,
                   ts.status_name AS ticket_status, bp.seat_number
            FROM booking_passengers bp
            JOIN passengers p ON bp.passenger_id = p.id
            JOIN ticket_status ts ON bp.ticket_status_id = ts.id
            WHERE bp.booking_id = %s
            """,
            (booking_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def cancel_booking(booking_id: int, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT flight_id FROM bookings WHERE id = %s AND user_id = %s",
            (booking_id, user_id),
        )
        booking = cursor.fetchone()

        if not booking:
            raise ValueError("Booking not found or access denied.")

        flight_id = booking[0]

        cancelled_status_id = get_status_id_by_name("booking", "Cancelled")

        cursor.execute(
            "UPDATE bookings SET booking_status_id = %s WHERE id = %s",
            (cancelled_status_id, booking_id),
        )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()