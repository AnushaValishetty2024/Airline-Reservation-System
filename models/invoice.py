from datetime import datetime
from models.user import get_db_connection


def create_invoice(booking_id: int, payment_id: int, total_amount: float):
    """Create invoice for a booking."""

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        invoice_number = "INV" + datetime.now().strftime("%Y%m%d%H%M%S")

        cursor.execute(
            """
            INSERT INTO invoices
            (booking_id, payment_id, invoice_number, total_amount, issued_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                booking_id,
                payment_id,
                invoice_number,
                total_amount,
                datetime.now(),
            ),
        )

        conn.commit()

        return {
            "id": cursor.lastrowid,
            "invoice_number": invoice_number,
        }

    finally:
        cursor.close()
        conn.close()