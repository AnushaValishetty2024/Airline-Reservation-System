from repositories.airline_repository import (
    get_all_airlines as db_get_all_airlines,
    count_airlines as db_count_airlines,
    get_airline_by_id as db_get_airline_by_id,
    get_airline_by_code as db_get_airline_by_code,
    create_airline as db_create_airline,
    update_airline as db_update_airline,
    delete_airline as db_delete_airline,
)


def get_all_airlines(status=None, page=1, per_page=10):
    """Get all airlines with optional status filter."""
    return db_get_all_airlines(status=status, page=page, per_page=per_page)


def count_airlines(status=None):
    """Count total airlines."""
    return db_count_airlines(status=status)


def get_airline_by_id(airline_id: int):
    """Get airline by ID."""
    return db_get_airline_by_id(airline_id)


def get_airline_by_code(airline_code: str):
    """Get airline by code."""
    return db_get_airline_by_code(airline_code)


def create_airline(airline_name: str, airline_code: str, country: str, status: str = "Active"):
    """Create a new airline."""
    if not airline_name or not airline_code or not country:
        raise ValueError("All fields are required.")
    existing = get_airline_by_code(airline_code)
    if existing:
        raise ValueError("Airline code already exists.")

    is_active = 1 if status == "Active" else 0
    db_create_airline(airline_name, airline_code, country, is_active)


def update_airline(airline_id: int, airline_name: str, airline_code: str, country: str, status: str):
    """Update an existing airline."""
    if not airline_name or not airline_code or not country:
        raise ValueError("All fields are required.")

    existing = get_airline_by_code(airline_code)
    if existing and existing["id"] != airline_id:
        raise ValueError("Airline code already exists.")

    is_active = 1 if status == "Active" else 0
    db_update_airline(airline_id, airline_name, airline_code, country, is_active)


def delete_airline(airline_id: int):
    """Delete an airline."""
    db_delete_airline(airline_id)


def toggle_airline_status(airline_id: int):
    """Toggle airline active/inactive status."""
    airline = get_airline_by_id(airline_id)
    if not airline:
        raise ValueError("Airline not found.")

    new_status = "Inactive" if airline["is_active"] else "Active"
    is_active = 1 if new_status == "Active" else 0
    db_update_airline(airline_id, airline["airline_name"], airline["airline_code"], airline["country"], is_active)
    return new_status