"""
Booking API Routes - JSON endpoints for booking operations.

Standardized JSON request format:
{
    "flight_id": 101,
    "passengers": [
        {"name": "Anusha", "age": 22},
        {"name": "Rahul", "age": 25}
    ]
}
"""

from flask import Blueprint, request, jsonify

from services.booking_service import create_booking
from core.exceptions import FlightNotFoundError, InsufficientSeatsError

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/api/book", methods=["POST"])
def api_book_flight():
    """
    Create a new booking via JSON API.

    Expected JSON payload:
    {
        "flight_id": 101,
        "seat_class": "economy",
        "passengers": [
            {"name": "Anusha", "age": 22},
            {"name": "Rahul", "age": 25}
        ]
    }

    Returns:
        JSON response with booking reference or error message
    """
    try:
        # Parse JSON request body
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON payload."}), 400

        # Validate top-level fields
        flight_id = data.get("flight_id")
        seat_class = data.get("seat_class", "economy")
        passengers_data = data.get("passengers", [])

        if not flight_id:
            return jsonify({"error": "flight_id is required."}), 400

        if not isinstance(passengers_data, list) or len(passengers_data) == 0:
            return jsonify({"error": "At least one passenger is required."}), 400

        # Validate each passenger
        for idx, pax in enumerate(passengers_data):
            if not isinstance(pax, dict):
                return jsonify({"error": f"Passenger {idx+1} must be an object."}), 400

            if not pax.get("name", "").strip():
                return jsonify({"error": f"Passenger {idx+1} name is required."}), 400

            if not pax.get("mobile", "").strip():
                return jsonify({"error": f"Passenger {idx+1} mobile number is required."}), 400

        # Calculate total amount
        from services.flight_service import get_flight_by_id
        flight = get_flight_by_id(flight_id)
        if not flight:
            return jsonify({"error": "Flight not found."}), 404

        base_price = (
            float(flight["economy_price"])
            if seat_class.lower() == "economy"
            else float(flight["business_price"])
        )
        total_amount = base_price * len(passengers_data)

        # Get user ID from session
        from flask import session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required."}), 401

        # Create booking
        booking_reference = create_booking(
            user_id=user_id,
            flight_id=flight_id,
            passengers_data=passengers_data,
            seat_class=seat_class,
            total_amount=total_amount,
        )

        return jsonify({
            "success": True,
            "booking_reference": booking_reference,
            "message": "Booking confirmed!",
        }), 201

    except FlightNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except InsufficientSeatsError as e:
        return jsonify({"error": str(e)}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Booking failed: {str(e)}"}), 500


@booking_bp.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    """
    Get booking history for the current user.

    Returns:
        JSON response with list of bookings
    """
    try:
        from services.booking_service import get_user_booking_history
        from flask import session

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required."}), 401

        bookings = get_user_booking_history(user_id)
        return jsonify({"bookings": bookings}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@booking_bp.route("/api/bookings/<int:booking_id>", methods=["GET"])
def api_get_booking_details(booking_id):
    """
    Get details of a specific booking.

    Returns:
        JSON response with booking details and passengers
    """
    try:
        from services.booking_service import (
            get_booking_details,
            get_booking_passengers_list,
        )

        booking = get_booking_details(booking_id)
        passengers = get_booking_passengers_list(booking_id)

        return jsonify({
            "booking": booking,
            "passengers": passengers,
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500