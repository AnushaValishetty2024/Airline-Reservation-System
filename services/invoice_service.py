import os
from datetime import datetime
from decimal import Decimal
from models.booking import get_booking_by_id, get_booking_passengers
from models.user import get_db_connection
from utils.pdf_generator import generate_pdf, build_invoice_content
from repositories.payment_repository import get_payment_by_booking_id


def create_invoice(booking_id: int) -> dict:
    """
    Generate a PDF invoice for a booking and save invoice record to DB.

    Args:
        booking_id: Booking ID

    Returns:
        dict with invoice information
    """
    conn = None
    cursor = None
    try:
        # Get booking details
        booking = get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        # Get payment details
        payment = get_payment_by_booking_id(booking_id)
        if not payment:
            raise ValueError("Payment not found for this booking")

        # Check if invoice already exists to avoid duplicates
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, invoice_number FROM invoices WHERE booking_id = %s", (booking_id,))
        existing_invoice = cursor.fetchone()
        if existing_invoice:
            return {
                "success": True,
                "booking_id": booking_id,
                "booking_reference": booking["booking_reference"],
                "invoice_number": existing_invoice["invoice_number"],
                "invoice_id": existing_invoice["id"],
                "amount": float(payment["amount"]),
                "payment_method": payment.get("payment_method"),
                "payment_status": payment.get("payment_status"),
                "message": "Invoice already exists"
            }

        # Get passengers (use first passenger for invoice)
        passengers = get_booking_passengers(booking_id)
        if not passengers:
            raise ValueError("No passengers found for this booking")

        primary_passenger = passengers[0]

        # Get pricing breakdown
        from services.pricing_service import get_pricing_breakdown
        pricing = get_pricing_breakdown(booking["flight_id"], "economy", len(passengers))

        if not pricing.get("success"):
            raise ValueError(pricing.get("error", "Failed to get pricing breakdown"))

        # Generate invoice number
        invoice_number = f"INV{booking['booking_reference']}{datetime.now().strftime('%Y%m%d')}"

        # Create invoices directory
        os.makedirs("invoices", exist_ok=True)

        # Prepare invoice data
        invoice_data = {
            "invoice_number": invoice_number,
            "booking_reference": booking["booking_reference"],
            "passenger_name": primary_passenger["full_name"],
            "payment_method": payment.get("payment_method", "N/A"),
            "transaction_id": payment.get("transaction_id", "N/A"),
            "payment_status": payment.get("payment_status", "Completed"),
            "flight_number": booking["flight_number"],
            "airline_name": booking["airline_name"],
            "origin_city": f"{booking['origin_city']} ({booking['origin_code']})",
            "destination_city": f"{booking['destination_city']} ({booking['destination_code']})",
            "base_fare": pricing.get("base_fare", 0),
            "taxes": pricing.get("taxes", 0),
            "gst": pricing.get("gst", 0),
            "convenience_fee": pricing.get("convenience_fee", 0),
            "grand_total": pricing.get("grand_total", 0),
        }

        # Generate filename
        filename = f"invoice_{booking['booking_reference']}.pdf"

        # Build PDF content
        def content_builder():
            return build_invoice_content(invoice_data)

        # Generate PDF
        filepath = generate_pdf(filename, content_builder, output_dir="invoices")

        if filepath:
            # Save invoice record to database
            cursor.execute(
                """
                INSERT INTO invoices (invoice_number, booking_id, payment_id)
                VALUES (%s, %s, %s)
                """,
                (invoice_number, booking_id, payment["id"])
            )
            invoice_id = cursor.lastrowid
            conn.commit()

            return {
                "success": True,
                "booking_id": booking_id,
                "booking_reference": booking["booking_reference"],
                "invoice_number": invoice_number,
                "invoice_id": invoice_id,
                "filename": filename,
                "filepath": filepath,
                "amount": float(payment["amount"]),
                "payment_method": payment.get("payment_method"),
                "payment_status": payment.get("payment_status"),
            }
        else:
            raise ValueError("Failed to generate PDF")

    except Exception as e:
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": str(e),
            "booking_id": booking_id,
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_invoice_path(booking_id: int) -> str:
    """
    Get the path to the most recent invoice for a booking.

    Args:
        booking_id: Booking ID

    Returns:
        File path to the invoice PDF
    """
    try:
        booking = get_booking_by_id(booking_id)
        if not booking:
            return None

        booking_reference = booking["booking_reference"]

        # Find invoice files for this booking
        if not os.path.exists("invoices"):
            return None

        # Look for invoice files - match both patterns: invoice_REF.pdf and invoice_REF_*.pdf
        files = [f for f in os.listdir("invoices") if f.startswith(f"invoice_{booking_reference}")]

        if not files:
            return None

        # Return most recent invoice
        files.sort(reverse=True)
        return os.path.join("invoices", files[0])

    except Exception as e:
        print(f"Error getting invoice path: {e}")
        return None


def regenerate_invoice(booking_id: int) -> dict:
    """
    Regenerate an invoice (creates a new version).

    Args:
        booking_id: Booking ID

    Returns:
        dict with result
    """
    return create_invoice(booking_id)


def get_invoice_info(booking_id: int) -> dict:
    """
    Get information about generated invoices for a booking.

    Args:
        booking_id: Booking ID

    Returns:
        dict with invoice information
    """
    try:
        booking = get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        booking_reference = booking["booking_reference"]

        if not os.path.exists("invoices"):
            return {
                "success": True,
                "booking_id": booking_id,
                "booking_reference": booking_reference,
                "invoices_count": 0,
                "invoices": [],
            }

        files = [f for f in os.listdir("invoices") if f.startswith(f"invoice_{booking_reference}_")]

        invoices = []
        for f in files:
            filepath = os.path.join("invoices", f)
            invoices.append({
                "filename": f,
                "filepath": filepath,
                "size_bytes": os.path.getsize(filepath),
                "created_at": datetime.fromtimestamp(
                    os.path.getctime(filepath)
                ).strftime("%Y-%m-%d %H:%M:%S"),
            })

        invoices.sort(key=lambda x: x["filename"], reverse=True)

        return {
            "success": True,
            "booking_id": booking_id,
            "booking_reference": booking_reference,
            "invoices_count": len(invoices),
            "invoices": invoices,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def validate_invoice_data(booking_id: int) -> dict:
    """
    Validate that all required data exists for invoice generation.

    Args:
        booking_id: Booking ID

    Returns:
        dict with validation result
    """
    errors = []

    # Check booking
    booking = get_booking_by_id(booking_id)
    if not booking:
        errors.append("Booking not found")
        return {"valid": False, "errors": errors}

    # Check payment
    payment = get_payment_by_booking_id(booking_id)
    if not payment:
        errors.append("Payment not found")
    elif payment.get("payment_status") != "Completed":
        errors.append("Payment is not completed")

    # Check passengers
    passengers = get_booking_passengers(booking_id)
    if not passengers:
        errors.append("No passengers found")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "booking_reference": booking.get("booking_reference") if booking else None,
    }