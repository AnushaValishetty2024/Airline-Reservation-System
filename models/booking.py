from mysql.connector import Error
from datetime import datetime
import random
import string

from models.user import get_db_connection


def generate_booking_reference():
    """Generate unique booking reference like BK123456."""
    return "BK" + "".join(random.choices(string.digits, k=6))


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


def create_booking(user_id, flight_id, passengers_data, seat_class, total_amount):
    """
    Create a booking with full transaction safety.
    
    Transaction flow:
    1. START TRANSACTION
    2. Validate flight exists and check seat availability (row-level lock)
    3. Create booking with PENDING status
    4. Insert passengers
    5. Allocate seats (mark as BOOKED)
    6. Update flight seat counts
    7. Update booking status to CONFIRMED
    8. COMMIT
    
    On any failure: ROLLBACK entire transaction
    """
    # Validate seat class
    if seat_class.lower() not in ["economy", "business"]:
        raise ValueError("Invalid seat class. Must be 'economy' or 'business'.")

    # Validate passengers data
    if not passengers_data or len(passengers_data) == 0:
        raise ValueError("At least one passenger is required.")

    for idx, pax in enumerate(passengers_data):
        if not isinstance(pax, dict):
            raise ValueError(f"Passenger {idx+1} must be an object.")
        if not pax.get("name", "").strip():
            raise ValueError(f"Passenger {idx+1} name is required.")
        # Optional fields: email, mobile, passport

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # STEP 1: Start transaction explicitly
        conn.start_transaction(isolation_level='SERIALIZABLE')
        
        # STEP 2: Validate flight exists and lock row for update
        cursor.execute(
            "SELECT seats_economy, seats_business FROM flights WHERE id = %s FOR UPDATE",
            (flight_id,),
        )
        flight = cursor.fetchone()
        if not flight:
            raise ValueError("Flight not found.")

        seats_economy, seats_business = flight
        passenger_count = len(passengers_data)

        if seat_class.lower() == "economy":
            if seats_economy < passenger_count:
                raise ValueError(f"Not enough economy seats. Available: {seats_economy}, Requested: {passenger_count}")
        elif seat_class.lower() == "business":
            if seats_business < passenger_count:
                raise ValueError(f"Not enough business seats. Available: {seats_business}, Requested: {passenger_count}")
        else:
            raise ValueError("Invalid seat class.")

        # STEP 3: Get status IDs
        pending_status_id = get_status_id_by_name("booking", "Pending")
        confirmed_status_id = get_status_id_by_name("booking", "Confirmed")
        payment_status_id = get_status_id_by_name("payment", "Paid")
        ticket_status_id = get_status_id_by_name("ticket", "Booked")

        if not all([pending_status_id, confirmed_status_id, payment_status_id, ticket_status_id]):
            raise ValueError("Required status seeds missing in database.")

        # DEBUG
        print(f"\n=== DEBUG: Creating Booking ===")
        print(f"Passenger Count: {passenger_count}")
        print(f"Received Passengers: {passengers_data}")
        print(f"Seat Class: {seat_class}")
        print(f"Total Amount: {total_amount}")

        # STEP 4: Create booking with PENDING status first
        booking_reference = generate_booking_reference()
        cursor.execute(
            "INSERT INTO bookings (booking_reference, user_id, flight_id, booking_status_id, total_amount) "
            "VALUES (%s, %s, %s, %s, %s)",
            (booking_reference, user_id, flight_id, pending_status_id, total_amount),
        )
        booking_id = cursor.lastrowid
        print(f"Booking ID: {booking_id}, Reference: {booking_reference}")

        # STEP 5: Insert passengers and booking_passengers
        inserted_passenger_ids = []
        for idx, pax in enumerate(passengers_data):
            print(f"  Inserting Passenger {idx+1}: {pax['name']}")
            cursor.execute(
                "INSERT INTO passengers (full_name, email, mobile_number, passport_number, gender, date_of_birth) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (pax["name"], pax["email"], pax["mobile"], pax.get("passport", "") or "",
                 pax.get("gender", "") or "", pax.get("dob", "") or ""),
            )
            passenger_id = cursor.lastrowid
            inserted_passenger_ids.append(passenger_id)

            cursor.execute(
                "INSERT INTO booking_passengers (booking_id, passenger_id, ticket_status_id, seat_number) "
                "VALUES (%s, %s, %s, %s)",
                (booking_id, passenger_id, ticket_status_id, pax.get("seat_number", "") or ""),
            )
            print(f"    Passenger ID: {passenger_id}, Seat: {pax.get('seat_number', 'N/A')}")

        print(f"Inserted Passenger IDs: {inserted_passenger_ids}")

        # STEP 6: Create payment record
        payment_reference = "PAY" + "".join(random.choices(string.digits, k=6))
        cursor.execute(
            "INSERT INTO payments (booking_id, payment_reference, amount, payment_method, payment_status_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (booking_id, payment_reference, total_amount, "Card", payment_status_id),
        )

        # STEP 7: Update flight seat counts
        if seat_class.lower() == "economy":
            cursor.execute(
                "UPDATE flights SET seats_economy = seats_economy - %s WHERE id = %s",
                (passenger_count, flight_id),
            )
        else:
            cursor.execute(
                "UPDATE flights SET seats_business = seats_business - %s WHERE id = %s",
                (passenger_count, flight_id),
            )

        # STEP 8: Update booking status to CONFIRMED
        cursor.execute(
            "UPDATE bookings SET booking_status_id = %s WHERE id = %s",
            (confirmed_status_id, booking_id),
        )

        # STEP 9: COMMIT transaction
        # STEP 9: COMMIT transaction
        conn.commit()

        return booking_id
    except Exception as e:
        # ROLLBACK on any error
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()
def get_booking_passengers(booking_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT p.id, p.full_name, p.email, p.mobile_number, p.passport_number,
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


def get_booking_history_enriched(user_id: int) -> list:
    """
    Get enriched booking history with payment, ticket, and invoice information.

    Args:
        user_id: User ID

    Returns:
        List of enriched booking dicts
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT 
                b.id, b.booking_reference, b.user_id, b.flight_id, 
                b.booking_status_id, b.total_amount, b.booked_at,
                bs.status_name AS booking_status,
                f.flight_number, f.departure_datetime, f.arrival_datetime,
                a.airline_name, 
                o.airport_code AS origin_code, o.city AS origin_city,
                d.airport_code AS destination_code, d.city AS destination_city,
                ac.aircraft_model,
                -- Payment info
                p.payment_reference,
                p.amount AS amount_paid,
                p.payment_method,
                p.paid_at AS payment_date,
                ps.status_name AS payment_status,
                -- Ticket info
                t.ticket_number,
                -- Invoice info
                inv.invoice_number
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            JOIN aircraft ac ON f.aircraft_id = ac.id
            -- LEFT JOINs to avoid failures when data is missing
            LEFT JOIN payments p ON p.booking_id = b.id
            LEFT JOIN payment_status ps ON p.payment_status_id = ps.id
            LEFT JOIN tickets t ON t.booking_id = b.id
            LEFT JOIN invoices inv ON inv.booking_id = b.id
            WHERE b.user_id = %s
            ORDER BY b.booked_at DESC
            """,
            (user_id,),
        )
        bookings = cursor.fetchall()
        return bookings

    finally:
        cursor.close()
        conn.close()

def cancel_booking(booking_id: int, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT flight_id FROM bookings WHERE id = %s AND user_id = %s",
            (booking_id, user_id),
        )
        booking = cursor.fetchone()

        if not booking:
            raise ValueError("Booking not found or access denied.")

        flight_id = booking["flight_id"]

        cancelled_status_id = get_status_id_by_name("booking", "Cancelled")

        if not cancelled_status_id:
            raise ValueError("Cancelled status not found in database.")

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
