from decimal import Decimal
from datetime import datetime

from models.user import get_db_connection


def get_payment_by_id(payment_id: int):
    """Get payment details by payment ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.id, p.payment_reference, p.booking_id, p.amount, 
               p.payment_method, p.transaction_id, p.payment_status_id, 
               p.paid_at, ps.status_name AS payment_status
        FROM payments p
        INNER JOIN payment_status ps ON p.payment_status_id = ps.id
        WHERE p.id = %s
        """,
        (payment_id,),
    )
    payment = cursor.fetchone()
    cursor.close()
    conn.close()
    return payment


def get_payment_by_booking_id(booking_id: int):
    """Get payment details by booking ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.id, p.payment_reference, p.booking_id, p.amount, 
               p.payment_method, p.transaction_id, p.payment_status_id, 
               p.paid_at, ps.status_name AS payment_status
        FROM payments p
        INNER JOIN payment_status ps ON p.payment_status_id = ps.id
        WHERE p.booking_id = %s
        """,
        (booking_id,),
    )
    payment = cursor.fetchone()
    cursor.close()
    conn.close()
    return payment


def create_payment(booking_id: int, amount: Decimal, payment_method: str, 
                   payment_status_id: int, transaction_id: str = None):
    """Create a new payment record."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Generate payment reference
        payment_reference = "PAY" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Check for duplicate payment for this booking
        cursor.execute(
            "SELECT id FROM payments WHERE booking_id = %s AND payment_status_id IN (1, 2)",
            (booking_id,)
        )
        existing = cursor.fetchone()
        if existing:
          return get_payment_by_booking_id(booking_id)
        
        cursor.execute(
            """
            INSERT INTO payments (booking_id, payment_reference, amount, payment_method, 
                                transaction_id, payment_status_id, paid_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (booking_id, payment_reference, amount, payment_method, 
             transaction_id, payment_status_id, datetime.now())
        )
        payment_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": payment_id,
            "payment_reference": payment_reference,
            "booking_id": booking_id,
            "amount": float(amount),
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "payment_status_id": payment_status_id,
            "paid_at": datetime.now()
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def update_payment_status(payment_id: int, payment_status_id: int, 
                          transaction_id: str = None):
    """Update payment status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if transaction_id:
            cursor.execute(
                "UPDATE payments SET payment_status_id = %s, transaction_id = %s, updated_at = %s WHERE id = %s",
                (payment_status_id, transaction_id, datetime.now(), payment_id)
            )
        else:
            cursor.execute(
                "UPDATE payments SET payment_status_id = %s, updated_at = %s WHERE id = %s",
                (payment_status_id, datetime.now(), payment_id)
            )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_payments_by_user(user_id: int, limit: int = 50, offset: int = 0):
    """Get all payments for a user with pagination."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.id, p.payment_reference, p.booking_id, p.amount, 
               p.payment_method, p.transaction_id, p.payment_status_id, 
               p.paid_at, ps.status_name AS payment_status,
               b.booking_reference, f.flight_number, 
               a.airline_name, o.city AS origin_city, d.city AS destination_city
        FROM payments p
        INNER JOIN payment_status ps ON p.payment_status_id = ps.id
        INNER JOIN bookings b ON p.booking_id = b.id
        INNER JOIN flights f ON b.flight_id = f.id
        INNER JOIN airlines a ON f.airline_id = a.id
        INNER JOIN airports o ON f.origin_airport_id = o.id
        INNER JOIN airports d ON f.destination_airport_id = d.id
        WHERE b.user_id = %s
        ORDER BY p.paid_at DESC
        LIMIT %s OFFSET %s
        """,
        (user_id, limit, offset)
    )
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return payments


def get_total_revenue():
    """Get total revenue from all completed payments using SQL aggregate."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT COUNT(*) AS total_transactions,
               COALESCE(SUM(amount), 0) AS total_revenue,
               COALESCE(AVG(amount), 0) AS average_payment,
               MIN(paid_at) AS first_payment_date,
               MAX(paid_at) AS last_payment_date
        FROM payments
        WHERE payment_status_id = 2  # Completed
        """
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_revenue_by_payment_method():
    """Get revenue breakdown by payment method using SQL GROUP BY."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT payment_method,
               COUNT(*) AS transaction_count,
               COALESCE(SUM(amount), 0) AS total_revenue,
               COALESCE(AVG(amount), 0) AS avg_amount
        FROM payments
        WHERE payment_status_id = 2  # Completed
        GROUP BY payment_method
        ORDER BY total_revenue DESC
        """
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_revenue_by_airline():
    """Get revenue breakdown by airline using SQL JOIN and GROUP BY."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT a.airline_name, a.airline_code,
               COUNT(DISTINCT p.id) AS total_bookings,
               COALESCE(SUM(p.amount), 0) AS total_revenue
        FROM payments p
        INNER JOIN bookings b ON p.booking_id = b.id
        INNER JOIN flights f ON b.flight_id = f.id
        INNER JOIN airlines a ON f.airline_id = a.id
        WHERE p.payment_status_id = 2  # Completed
        GROUP BY a.id, a.airline_name, a.airline_code
        ORDER BY total_revenue DESC
        """
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_payment_status_distribution():
    """Get payment status distribution using SQL CASE and GROUP BY."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT 
            CASE 
                WHEN ps.status_name = 'Completed' THEN 'Completed'
                WHEN ps.status_name = 'Pending' THEN 'Pending'
                WHEN ps.status_name = 'Failed' THEN 'Failed'
                WHEN ps.status_name = 'Refunded' THEN 'Refunded'
                ELSE 'Other'
            END AS status_category,
            COUNT(*) AS count,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM payments p
        INNER JOIN payment_status ps ON p.payment_status_id = ps.id
        GROUP BY status_category
        ORDER BY count DESC
        """
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_daily_revenue_report(days: int = 30):
    """Get daily revenue report for the last N days using SQL DATE and GROUP BY."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT DATE(paid_at) AS payment_date,
               COUNT(*) AS transaction_count,
               COALESCE(SUM(amount), 0) AS daily_revenue
        FROM payments
        WHERE payment_status_id = 2
          AND paid_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(paid_at)
        ORDER BY payment_date DESC
        """,
        (days,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def refund_payment(payment_id: int, refund_reason: str = None):
    """Process a refund by updating payment status to Refunded."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get current payment
        cursor.execute("SELECT payment_status_id, amount FROM payments WHERE id = %s", (payment_id,))
        payment = cursor.fetchone()
        if not payment:
            raise ValueError("Payment not found")
        
        # Check if payment is completed
        if payment["payment_status_id"] != 2:  # Not Completed
            raise ValueError("Only completed payments can be refunded")
        
        # Get refund status ID (assuming it exists)
        cursor.execute("SELECT id FROM payment_status WHERE status_name = 'Refunded'")
        refund_status = cursor.fetchone()
        if not refund_status:
            raise ValueError("Refund status not found in database")
        
        refund_status_id = refund_status["id"]
        
        # Update payment status
        cursor.execute(
            "UPDATE payments SET payment_status_id = %s, updated_at = %s WHERE id = %s",
            (refund_status_id, datetime.now(), payment_id)
        )
        conn.commit()
        
        return {
            "success": True,
            "payment_id": payment_id,
            "refund_amount": float(payment["amount"]),
            "refund_reason": refund_reason
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_payment_report_summary():
    """Get payment summary for admin dashboard."""
    from models.user import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_transactions,
                COALESCE(SUM(amount), 0) AS total_revenue,
                COALESCE(AVG(amount), 0) AS average_payment,
                SUM(CASE WHEN payment_status_id = 2 THEN 1 ELSE 0 END) AS successful_payments,
                SUM(CASE WHEN payment_status_id = 3 THEN 1 ELSE 0 END) AS failed_payments
            FROM payments
        """)

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()