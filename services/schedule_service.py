from repositories.schedule_repository import (
    get_all_schedules as db_get_all_schedules,
    count_schedules as db_count_schedules,
    get_schedule_by_id as db_get_schedule_by_id,
    get_schedules_by_flight as db_get_schedules_by_flight,
    create_schedule as db_create_schedule,
    update_schedule as db_update_schedule,
    delete_schedule as db_delete_schedule,
)


def get_all_schedules(status=None, page=1, per_page=10):
    """Get all schedules with optional status filter."""
    return db_get_all_schedules(status=status, page=page, per_page=per_page)


def count_schedules(status=None):
    """Count total schedules."""
    return db_count_schedules(status=status)


def get_schedule_by_id(schedule_id: int):
    """Get schedule by ID."""
    return db_get_schedule_by_id(schedule_id)


def get_schedules_by_flight(flight_id: int):
    """Get schedules for a flight."""
    return db_get_schedules_by_flight(flight_id)


def create_schedule_service(flight_id: int, departure_time: str, arrival_time: str, price: float, terminal: str = None, gate_number: str = None, status: str = "Scheduled"):
    """Create a new schedule."""
    if not flight_id:
        raise ValueError("Flight is required.")
    if not departure_time or not arrival_time:
        raise ValueError("Departure and arrival times are required.")
    if arrival_time <= departure_time:
        raise ValueError("Arrival time must be after departure time.")
    if not price or price <= 0:
        raise ValueError("Price must be greater than zero.")

    db_create_schedule(flight_id, departure_time, arrival_time, price, terminal, gate_number, status)


def update_schedule_service(schedule_id: int, flight_id: int, departure_time: str, arrival_time: str, price: float, terminal: str = None, gate_number: str = None, status: str = "Scheduled"):
    """Update an existing schedule."""
    if not flight_id:
        raise ValueError("Flight is required.")
    if not departure_time or not arrival_time:
        raise ValueError("Departure and arrival times are required.")
    if arrival_time <= departure_time:
        raise ValueError("Arrival time must be after departure time.")
    if not price or price <= 0:
        raise ValueError("Price must be greater than zero.")

    db_update_schedule(schedule_id, flight_id, departure_time, arrival_time, price, terminal, gate_number, status)


def delete_schedule_service(schedule_id: int):
    """Delete a schedule."""
    db_delete_schedule(schedule_id)