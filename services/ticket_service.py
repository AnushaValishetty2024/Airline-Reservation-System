import os
from datetime import datetime
from models.booking import get_booking_by_id, get_booking_passengers
from models.user import get_db_connection
from utils.pdf_generator import generate_pdf, build_ticket_content
from utils.qr_generator import generate_booking_qr


def generate_ticket_number(booking_reference: str, passenger_id: int) -> str:
    """Generate unique ticket number like TK{booking_reference}{passenger_id}."""
    return f"TK{booking_reference}{passenger_id}"


def create_ticket(booking_id: int, passenger_id: int = None) -> dict:
    """
    Generate a PDF ticket for a booking and save ticket record to DB.

    Args:
        booking_id: Booking ID
        passenger_id: Optional specific passenger ID (if None, generate for all)

    Returns:
        dict with ticket information
    """
    conn = None
    cursor = None
    try:
        # Get booking details
        booking = get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        # Get passengers
        passengers = get_booking_passengers(booking_id)
        if not passengers:
            raise ValueError("No passengers found for this booking")

        # If specific passenger requested, filter
        if passenger_id:
            passengers = [p for p in passengers if p["id"] == passenger_id]
            if not passengers:
                raise ValueError("Passenger not found in this booking")

        # Check for existing tickets to avoid duplicates
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ticket_number FROM tickets WHERE booking_id = %s", (booking_id,))
        existing_tickets = {row["ticket_number"] for row in cursor.fetchall()}

        generated_tickets = []

        for idx, passenger in enumerate(passengers):
            ticket_number = generate_ticket_number(booking["booking_reference"], passenger["id"])

            # Skip if ticket already exists
            if ticket_number in existing_tickets:
                continue

            # Generate QR code
            qr_result = generate_booking_qr(booking["booking_reference"], booking_id)

            # Create tickets directory
            os.makedirs("tickets", exist_ok=True)

            # Prepare ticket data
            ticket_data = {
                "ticket_number": ticket_number,
                "booking_reference": booking["booking_reference"],
                "passenger_name": passenger["full_name"],
                "flight_number": booking["flight_number"],
                "airline_name": booking["airline_name"],
                "origin_city": f"{booking['origin_city']} ({booking['origin_code']})",
                "destination_city": f"{booking['destination_city']} ({booking['destination_code']})",
                "departure_time": booking["departure_datetime"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(booking["departure_datetime"], datetime) else str(booking["departure_datetime"]),
                "arrival_time": booking["arrival_datetime"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(booking["arrival_datetime"], datetime) else str(booking["arrival_datetime"]),
                "seat_number": passenger.get("seat_number", "Not Assigned"),
                "seat_class": "Economy",
                "booking_status": booking["booking_status"],
                "gate": "A1",
                "boarding_time": (booking["departure_datetime"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(booking["departure_datetime"], datetime) else str(booking["departure_datetime"])),
                "qr_image": qr_result.get("qr_image") if qr_result.get("qr_image") else None,
            }

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"ticket_{booking['booking_reference']}_{passenger['id']}_{timestamp}.pdf"

            # Build PDF content
            def content_builder():
                return build_ticket_content(ticket_data)

            # Generate PDF
            filepath = generate_pdf(filename, content_builder, output_dir="tickets")

            if filepath:
                # Save ticket record to database
                cursor.execute(
                    """
                    INSERT INTO tickets (ticket_number, booking_id, passenger_id, qr_code, issued_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (ticket_number, booking_id, passenger["id"], qr_result.get("qr_image"), datetime.now())
                )
                conn.commit()

                generated_tickets.append({
                    "ticket_id": cursor.lastrowid,
                    "ticket_number": ticket_number,
                    "passenger_id": passenger["id"],
                    "passenger_name": passenger["full_name"],
                    "filename": filename,
                    "filepath": filepath,
                    "booking_reference": booking["booking_reference"],
                })

        return {
            "success": True,
            "booking_id": booking_id,
            "booking_reference": booking["booking_reference"],
            "tickets_generated": len(generated_tickets),
            "tickets": generated_tickets,
        }

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


def get_ticket_path(booking_id: int, passenger_id: int = None) -> str:
    """
    Get the path to the most recent ticket for a booking.

    Args:
        booking_id: Booking ID
        passenger_id: Optional passenger ID

    Returns:
        File path to the ticket PDF
    """
    try:
        booking = get_booking_by_id(booking_id)
        if not booking:
            return None

        booking_reference = booking["booking_reference"]

        # Find ticket files for this booking
        if not os.path.exists("tickets"):
            return None

        files = [f for f in os.listdir("tickets") if f.startswith(f"ticket_{booking_reference}_")]

        if not files:
            return None

        # If passenger_id specified, find exact match
        if passenger_id:
            matching = [f for f in files if f"_{passenger_id}_" in f]
            if matching:
                # Return most recent
                matching.sort(reverse=True)
                return os.path.join("tickets", matching[0])

        # Return most recent ticket for this booking
        files.sort(reverse=True)
        return os.path.join("tickets", files[0])

    except Exception as e:
        print(f"Error getting ticket path: {e}")
        return None


def regenerate_ticket(booking_id: int, passenger_id: int = None) -> dict:
    """
    Regenerate a ticket (creates a new version).

    Args:
        booking_id: Booking ID
        passenger_id: Optional passenger ID

    Returns:
        dict with result
    """
    return create_ticket(booking_id, passenger_id)


def get_ticket_info(booking_id: int) -> dict:
    """
    Get information about generated tickets for a booking.

    Args:
        booking_id: Booking ID

    Returns:
        dict with ticket information
    """
    try:
        booking = get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        booking_reference = booking["booking_reference"]

        if not os.path.exists("tickets"):
            return {
                "success": True,
                "booking_id": booking_id,
                "booking_reference": booking_reference,
                "tickets_count": 0,
                "tickets": [],
            }

        files = [f for f in os.listdir("tickets") if f.startswith(f"ticket_{booking_reference}_")]

        # Group by passenger
        passenger_tickets = {}
        for f in files:
            parts = f.replace(".pdf", "").split("_")
            if len(parts) >= 3:
                pax_id = parts[2]
                if pax_id not in passenger_tickets:
                    passenger_tickets[pax_id] = []
                passenger_tickets[pax_id].append({
                    "filename": f,
                    "filepath": os.path.join("tickets", f),
                    "size_bytes": os.path.getsize(os.path.join("tickets", f)),
                })

        # Sort each passenger's tickets by filename (timestamp)
        for pax_id in passenger_tickets:
            passenger_tickets[pax_id].sort(key=lambda x: x["filename"], reverse=True)

        return {
            "success": True,
            "booking_id": booking_id,
            "booking_reference": booking_reference,
            "tickets_count": len(files),
            "passenger_tickets": passenger_tickets,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }