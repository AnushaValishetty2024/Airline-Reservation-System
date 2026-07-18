from core.exceptions import (
    FlightNotFoundError,
    InsufficientSeatsError,
    InvalidSeatClassError,
    MissingStatusError,
)
from repositories.booking_repository import (
    get_booking_by_id,
    get_user_bookings,
    get_booking_passengers,
    get_flight_seats,
    cancel_booking as db_cancel_booking,
)


def create_booking(user_id: int, flight_id: int, passengers_data: list, seat_class: str, total_amount: float) -> str:
    """
    Create a complete booking with passengers and payment.
    
    This function delegates to the model layer which handles the full transaction.
    Returns booking reference.
    
    Transaction flow (handled in models/booking.py):
    1. START TRANSACTION with SERIALIZABLE isolation
    2. Validate flight exists and check seat availability (row-level lock via FOR UPDATE)
    3. Create booking with PENDING status
    4. Insert passengers
    5. Link passengers to booking via booking_passengers
    6. Create payment record
    7. Update flight seat counts
    8. Update booking status to CONFIRMED
    9. COMMIT
    
    On any failure: ROLLBACK entire transaction
    """
    # Validate seat class
    if seat_class.lower() not in ["economy", "business"]:
        raise InvalidSeatClassError("Invalid seat class. Must be 'economy' or 'business'.")

    # Validate passengers data
    if not passengers_data or len(passengers_data) == 0:
        raise ValueError("At least one passenger is required.")

    for idx, pax in enumerate(passengers_data):
        if not isinstance(pax, dict):
            raise ValueError(f"Passenger {idx+1} must be an object.")
        if not pax.get("name", "").strip():
            raise ValueError(f"Passenger {idx+1} name is required.")
        # Optional fields (email, mobile, passport) can be empty

    # Import the transaction-aware booking function
    from models.booking import create_booking as create_booking_transaction
    
    # Delegate to model layer which handles full transaction
    booking_reference = create_booking_transaction(
        user_id, flight_id, passengers_data, seat_class, total_amount
    )
    
    return booking_reference


def get_booking_details(booking_id: int):
    """Get booking details by ID."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise ValueError("Booking not found.")
    return booking


def get_user_booking_history(user_id: int):
    """Get all bookings for a user."""
    return get_user_bookings(user_id)


def get_booking_passengers_list(booking_id: int):
    """Get passengers for a booking."""
    return get_booking_passengers(booking_id)


def cancel_booking_service(booking_id: int, user_id: int):
    """Cancel a booking."""
    db_cancel_booking(booking_id, user_id)