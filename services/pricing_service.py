from datetime import datetime, date
from decimal import Decimal

from models.user import get_db_connection


def calculate_dynamic_price(flight_id: int, seat_class: str = "economy") -> dict:
    """
    Calculate dynamic ticket price based on multiple factors.

    Formula:
    Current Price = Base Price × Weekend Multiplier × Holiday Multiplier × Seat Availability Multiplier

    Args:
        flight_id: Flight ID
        seat_class: 'economy' or 'business'

    Returns:
        dict with price calculation details
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get base price
        query = """
            SELECT f.id, f.economy_price, f.business_price,
                   f.seats_economy, f.seats_business,
                   ac.seating_capacity,
                   f.departure_datetime
            FROM flights f
            INNER JOIN aircraft ac ON f.aircraft_id = ac.id
            WHERE f.id = %s
        """
        cursor.execute(query, (flight_id,))
        flight = cursor.fetchone()

        if not flight:
            return {"success": False, "error": "Flight not found"}

        base_price = float(flight["economy_price"] if seat_class.lower() == "economy" else flight["business_price"])
        departure_dt = flight["departure_datetime"]

        # Step 1: Get multipliers
        weekend_multiplier = apply_weekend_pricing(departure_dt)
        holiday_multiplier = apply_holiday_pricing(departure_dt)
        seat_multiplier = apply_seat_availability_pricing(flight, seat_class)

        # Step 2: Calculate final price
        current_price = base_price * weekend_multiplier * holiday_multiplier * seat_multiplier

        # Step 3: Round to 2 decimal places
        current_price = round(current_price, 2)

        # Step 4: Update flight with current_price
        update_current_price(flight_id, current_price, seat_class)

        return {
            "success": True,
            "flight_id": flight_id,
            "seat_class": seat_class,
            "base_price": base_price,
            "weekend_multiplier": weekend_multiplier,
            "holiday_multiplier": holiday_multiplier,
            "seat_availability_multiplier": seat_multiplier,
            "current_price": current_price,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def apply_weekend_pricing(departure_datetime) -> float:
    """
    Apply weekend pricing multiplier.

    Returns 1.15 if departure is on Saturday (5) or Sunday (6), else 1.00.
    """
    weekday = departure_datetime.weekday()
    if weekday >= 5:  # Saturday or Sunday
        return 1.15
    return 1.00


def apply_holiday_pricing(departure_datetime) -> float:
    """
    Apply holiday pricing multiplier.

    Returns 1.20 if departure date is a holiday, else 1.00.
    """
    departure_date = departure_datetime.date()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT COUNT(*) as count FROM holidays WHERE holiday_date = %s",
            (departure_date,),
        )
        result = cursor.fetchone()
        if result and result["count"] > 0:
            return 1.20
        return 1.00
    finally:
        cursor.close()
        conn.close()


def apply_seat_availability_pricing(flight: dict, seat_class: str) -> float:
    """
    Apply seat availability pricing multiplier.

    Returns 1.25 if less than 20% seats available, else 1.00.
    """
    if seat_class.lower() == "economy":
        total_seats = float(flight.get("seating_capacity", 0))
        available_seats = float(flight.get("seats_economy", 0))
    else:
        # For business class, use business seats vs total capacity approximation
        total_seats = float(flight.get("seating_capacity", 0))
        available_seats = float(flight.get("seats_business", 0))

    if total_seats <= 0:
        return 1.00

    availability_ratio = available_seats / total_seats

    if availability_ratio < 0.20:
        return 1.25
    return 1.00


def update_current_price(flight_id: int, current_price: float, seat_class: str):
    """
    Update the flight's current_price and last_price_update in database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the base price column for the relevant seat class
        if seat_class.lower() == "economy":
            cursor.execute(
                "UPDATE flights SET current_price = %s, last_price_update = NOW() WHERE id = %s",
                (current_price, flight_id),
            )
        else:
            cursor.execute(
                "UPDATE flights SET current_price = %s, last_price_update = NOW() WHERE id = %s",
                (current_price, flight_id),
            )

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_pricing_breakdown(flight_id: int, seat_class: str, passenger_count: int) -> dict:
    """
    Get full pricing breakdown for payment page.

    Args:
        flight_id: Flight ID
        seat_class: 'economy' or 'business'
        passenger_count: Number of passengers

    Returns:
        dict with fare breakdown
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get flight details
        cursor.execute(
            """
            SELECT f.economy_price, f.business_price, f.current_price,
                   a.airline_name, f.flight_number
            FROM flights f
            INNER JOIN airlines a ON f.airline_id = a.id
            WHERE f.id = %s
            """,
            (flight_id,),
        )
        flight = cursor.fetchone()

        if not flight:
            return {"success": False, "error": "Flight not found"}

        base_price = float(flight["economy_price"] if seat_class.lower() == "economy" else flight["business_price"])
        current_price_per_person = float(flight.get("current_price") or base_price)

        # Calculate components
        base_fare = base_price * passenger_count
        taxes = round(base_fare * 0.05, 2)  # 5% tax
        gst = round(base_fare * 0.05, 2)    # 5% GST
        convenience_fee = round(base_fare * 0.02, 2)  # 2% convenience fee

        # If dynamic pricing changed the price per person, calculate final total
        total_base = current_price_per_person * passenger_count

        # Recalculate taxes and fees on dynamic total
        taxes = round(total_base * 0.05, 2)
        gst = round(total_base * 0.05, 2)
        convenience_fee = round(total_base * 0.02, 2)

        grand_total = round(total_base + taxes + gst + convenience_fee, 2)

        return {
            "success": True,
            "airline_name": flight["airline_name"],
            "flight_number": flight["flight_number"],
            "seat_class": seat_class,
            "passenger_count": passenger_count,
            "base_fare_per_person": base_price,
            "current_price_per_person": current_price_per_person,
            "base_fare": base_fare,
            "taxes": taxes,
            "gst": gst,
            "convenience_fee": convenience_fee,
            "grand_total": grand_total,
        }

    finally:
        cursor.close()
        conn.close()


def recalculate_flight_prices():
    """
    Recalculate current_price for all flights that haven't been updated recently.
    Scheduled task helper.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Find flights with stale or NULL prices
        cursor.execute(
            """
            SELECT id, departure_datetime, economy_price, business_price,
                   seats_economy, seats_business, seating_capacity
            FROM flights f
            INNER JOIN aircraft ac ON f.aircraft_id = ac.id
            WHERE last_price_update IS NULL OR last_price_update < NOW() - INTERVAL 1 DAY
            """
        )
        flights = cursor.fetchall()

        updated = 0
        for flight in flights:
            for seat_class in ["economy", "business"]:
                result = calculate_dynamic_price(flight["id"], seat_class)
                if result.get("success"):
                    updated += 1

        return {"success": True, "flights_updated": updated}

    finally:
        cursor.close()
        conn.close()