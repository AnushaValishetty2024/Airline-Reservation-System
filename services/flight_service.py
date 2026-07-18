from repositories.flight_repository import (
    get_airlines as db_get_airlines,
    get_airports as db_get_airports,
    get_aircraft as db_get_aircraft,
    get_all_flights as db_get_all_flights,
    get_flight_by_id as db_get_flight_by_id,
    search_flights as db_search_flights,
    create_flight as db_create_flight,
    update_flight as db_update_flight,
    delete_flight as db_delete_flight,
)


def get_airlines():
    """Get all active airlines."""
    return db_get_airlines()


def get_airports():
    """Get all active airports."""
    return db_get_airports()


def get_aircraft():
    """Get all active aircraft."""
    return db_get_aircraft()


def search_flights(origin_id=None, destination_id=None, departure_date=None, sort_by="departure_datetime",
                   airline_id=None, min_price=None, max_price=None, time_of_day=None, passenger_count=1):
    """Search flights with filters."""
    return db_search_flights(
        origin_id=origin_id,
        destination_id=destination_id,
        departure_date=departure_date,
        sort_by=sort_by,
        airline_id=airline_id,
        min_price=min_price,
        max_price=max_price,
        time_of_day=time_of_day,
        passenger_count=passenger_count,
    )


def get_flight_by_id(flight_id: int):
    """Get flight details by ID."""
    flight = db_get_flight_by_id(flight_id)
    if not flight:
        raise ValueError("Flight not found.")
    return flight


def get_all_flights():
    """Get all flights."""
    return db_get_all_flights()


def create_flight_service(flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
                          departure_datetime, arrival_datetime, economy_price, business_price, status):
    """Create a new flight."""
    if not flight_number or not airline_id or not aircraft_id:
        raise ValueError("Flight number, airline, and aircraft are required.")
    if departure_datetime >= arrival_datetime:
        raise ValueError("Arrival time must be after departure time.")
    if economy_price <= 0 or business_price <= 0:
        raise ValueError("Prices must be greater than zero.")

    db_create_flight(
        flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
        departure_datetime, arrival_datetime, economy_price, business_price, status,
    )


def update_flight_service(flight_id, flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
                          departure_datetime, arrival_datetime, economy_price, business_price, status):
    """Update an existing flight."""
    if not flight_number or not airline_id or not aircraft_id:
        raise ValueError("Flight number, airline, and aircraft are required.")
    if departure_datetime >= arrival_datetime:
        raise ValueError("Arrival time must be after departure time.")
    if economy_price <= 0 or business_price <= 0:
        raise ValueError("Prices must be greater than zero.")

    db_update_flight(
        flight_id, flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
        departure_datetime, arrival_datetime, economy_price, business_price, status,
    )


def delete_flight_service(flight_id: int):
    """Delete a flight."""
    db_delete_flight(flight_id)


def toggle_flight_status_service(flight_id: int):
    """Toggle flight active/inactive status."""
    from repositories.flight_repository import toggle_flight_status
    return toggle_flight_status(flight_id)
