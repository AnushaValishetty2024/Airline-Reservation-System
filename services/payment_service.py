from decimal import Decimal
from datetime import datetime
import uuid
import secrets
import traceback

from repositories.payment_repository import (
    get_payment_by_id,
    get_payment_by_booking_id,
    create_payment,
    update_payment_status,
    get_payments_by_user,
)
from models.user import get_db_connection
from services.ticket_service import create_ticket
from services.invoice_service import create_invoice


# Constants
PAYMENT_STATUS = {
    "PENDING": 1,
    "COMPLETED": 2,
    "FAILED": 3,
    "REFUNDED": 4
}

ALLOWED_METHODS = [
    "Credit Card",
    "Debit Card",
    "PhonePe (UPI)",
    "Google Pay (UPI)",
    "Paytm (UPI)",
    "BHIM UPI",
    "Net Banking",
]

def validate_payment_method(payment_method: str) -> bool:
    """Validate that the payment method is allowed."""
    if not payment_method:
        return False
    return payment_method in ALLOWED_METHODS


def validate_payment_amount(amount) -> Decimal:
    """Validate and convert payment amount to Decimal."""
    try:
        amount = Decimal(str(amount))
    except (ValueError, TypeError):
        raise ValueError("Invalid payment amount")

    if amount <= 0:
        raise ValueError("Payment amount must be greater than 0")

    if amount > Decimal("999999.99"):
        raise ValueError("Payment amount exceeds maximum allowed")

    return amount


def process_payment(booking_id: int, amount: Decimal, payment_method: str) -> dict:
    print("DEBUG: process_payment() called")
    """
    Process a payment for a booking.

    Args:
        booking_id: Booking ID
        amount: Payment amount
        payment_method: Credit Card, Debit Card, UPI, Net Banking

    Returns:
        dict with payment result
    """
    try:
        # Validate inputs
        if not validate_payment_method(payment_method):
            return {
                "success": False,
                "error": f"Invalid payment method. Allowed: {', '.join(ALLOWED_METHODS)}"
            }

        amount = validate_payment_amount(amount)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Validate booking exists and is confirmable
        cursor.execute(
            """
            SELECT b.id, b.booking_reference, b.total_amount, b.user_id,
                   bs.status_name AS booking_status
            FROM bookings b
            INNER JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.id = %s
            """,
            (booking_id,),
        )
        booking = cursor.fetchone()
        cursor.close()
        conn.close()

        if not booking:
            return {"success": False, "error": "Invalid booking"}

        if booking["booking_status"] == "Cancelled":
            return {"success": False, "error": "Cannot process payment for cancelled booking"}

        if booking["booking_status"] == "Confirmed":
            existing_payment = get_payment_by_booking_id(booking_id)
            if existing_payment and existing_payment.get("payment_status") == "Completed":
                return {
                    "success": False,
                    "error": "Payment already completed for this booking",
                    "payment_id": existing_payment.get("id")
                }

        # Simulate payment gateway
                # Simulate payment gateway
        payment_result = simulate_payment_gateway(amount, payment_method)

        if payment_result["success"]:
            transaction_id = payment_result["transaction_id"]
            payment_status_id = PAYMENT_STATUS["COMPLETED"]
        else:
            transaction_id = None
            payment_status_id = PAYMENT_STATUS["FAILED"]

        # Record payment
        payment = create_payment(
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            payment_status_id=payment_status_id,
            transaction_id=transaction_id,
        )

        # Create ticket and invoice only if payment was successful
        if payment_result["success"]:
            print("DEBUG: Creating ticket...")

            ticket = create_ticket(
                booking_id=booking_id
            )

            print("DEBUG: Ticket created:", ticket)

            print("DEBUG: Creating invoice...")

            invoice = create_invoice(
                booking_id=booking_id
            )

            print("DEBUG: Invoice created:", invoice)

        return {
            "success": payment_result["success"],
            "payment_id": payment["id"],
            "payment_reference": payment["payment_reference"],
            "transaction_id": transaction_id,
            "amount": float(amount),
            "payment_method": payment_method,
            "payment_status": "Completed" if payment_result["success"] else "Failed",
            "booking_reference": booking["booking_reference"],
            "message": payment_result["message"]
        }
    except ValueError as e:
        raise e

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Payment processing failed: {str(e)}"
        }
def simulate_payment_gateway(amount: Decimal, payment_method: str) -> dict:
    """
    Simulate payment gateway processing.

    Args:
        amount: Payment amount
        payment_method: Payment method

    Returns:
        dict with simulated payment result
    """
    try:
        # Simulate 90% success rate
        import random
        success = random.random() < 0.90

        transaction_id = str(uuid.uuid4()).replace("-", "")[:16].upper()

        if success:
            return {
                "success": True,
                "transaction_id": f"TXN{transaction_id}",
                "message": "Payment processed successfully"
            }
        else:
            error_reasons = [
                "Insufficient funds",
                "Card declined",
                "Transaction timeout",
                "Bank unavailable"
            ]
            return {
                "success": False,
                "transaction_id": None,
                "message": random.choice(error_reasons)
            }

    except Exception as e:
        return {
            "success": False,
            "transaction_id": None,
            "message": f"Payment gateway error: {str(e)}"
        }


def get_payment_details(payment_id: int) -> dict:
    """Get payment details by ID."""
    payment = get_payment_by_id(payment_id)
    if not payment:
        raise ValueError("Payment not found")
    return payment


def get_user_payment_history(user_id: int, page: int = 1, page_size: int = 20):
    """Get payment history for a user with pagination."""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    offset = (page - 1) * page_size
    payments = get_payments_by_user(user_id, limit=page_size, offset=offset)

    return {
        "payments": payments,
        "page": page,
        "page_size": page_size,
        "total": len(payments)
    }


def initiate_refund(payment_id: int, refund_reason: str = None) -> dict:
    """
    Initiate a refund for a payment.

    Args:
        payment_id: Payment ID
        refund_reason: Reason for refund

    Returns:
        dict with refund result
    """
    from repositories.payment_repository import refund_payment

    try:
        result = refund_payment(payment_id, refund_reason)
        return {
            "success": True,
            "payment_id": payment_id,
            "refund_amount": result["refund_amount"],
            "message": "Refund processed successfully"
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Refund failed: {str(e)}"}


def get_payment_methods():
    """Get list of allowed payment methods."""
    return [{"id": method, "name": method} for method in ALLOWED_METHODS]


def validate_payment_statuses():
    """Ensure required payment statuses exist in database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, status_name FROM payment_status")
        existing_statuses = {row["status_name"]: row["id"] for row in cursor.fetchall()}

        required_statuses = ["Pending", "Completed", "Failed", "Refunded"]
        missing_statuses = [s for s in required_statuses if s not in existing_statuses]

        return {
            "success": len(missing_statuses) == 0,
            "missing_statuses": missing_statuses,
            "existing_statuses": existing_statuses
        }
    finally:
        cursor.close()
        conn.close()


def get_payment_report_summary():
    """
    Get comprehensive payment report using SQL aggregates.

    Returns summary with totals, averages, and status distribution.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Total revenue
        cursor.execute(
            """
            SELECT COUNT(*) AS total_transactions,
                   COALESCE(SUM(amount), 0) AS total_revenue,
                   COALESCE(AVG(amount), 0) AS avg_transaction,
                   MIN(paid_at) AS first_payment,
                   MAX(paid_at) AS last_payment
            FROM payments
            WHERE payment_status_id = 2
            """
        )
        summary = cursor.fetchone()

        # Status distribution
        cursor.execute(
            """
            SELECT ps.status_name,
                   COUNT(*) AS count,
                   COALESCE(SUM(p.amount), 0) AS total_amount
            FROM payments p
            INNER JOIN payment_status ps ON p.payment_status_id = ps.id
            GROUP BY ps.status_name
            ORDER BY count DESC
            """
        )
        status_dist = cursor.fetchall()

        # Method breakdown
        cursor.execute(
            """
            SELECT payment_method,
                   COUNT(*) AS count,
                   COALESCE(SUM(amount), 0) AS total_amount
            FROM payments
            WHERE payment_status_id = 2
            GROUP BY payment_method
            ORDER BY total_amount DESC
            """
        )
        method_breakdown = cursor.fetchall()

        return {
            "success": True,
            "summary": summary,
            "status_distribution": status_dist,
            "method_breakdown": method_breakdown
        }
    finally:
        cursor.close()
        conn.close()


def log_payment_audit(user_id: int, action: str, entity_type: str, entity_id: int, details: str):
    """Log payment-related actions for audit."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, entity_type, entity_id, details, datetime.now())
        )
        conn.commit()
    except Exception as e:
        print(f"Audit log error: {e}")
    finally:
        cursor.close()
        conn.close()