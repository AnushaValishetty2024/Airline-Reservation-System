from datetime import datetime
from models.user import get_db_connection


def create_ticket(booking_id: int, seat_number: str = None):
    """Create a ticket for a booking."""

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        ticket_number = "TKT" + datetime.now().strftime("%Y%m%d%H%M%S")

        cursor.execute(
            """
            INSERT INTO tickets
            (booking_id, ticket_number, seat_number, issued_at)
            VALUES (%s, %s, %s, %s)
            """,
            (
                booking_id,
                ticket_number,
                seat_number,
                datetime.now(),
            ),
        )

        conn.commit()

        return {
            "id": cursor.lastrowid,
            "ticket_number": ticket_number,
        }

    finally:
        cursor.close()
        conn.close()