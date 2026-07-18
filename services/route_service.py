from repositories.route_repository import (
    get_all_routes as db_get_all_routes,
    count_routes as db_count_routes,
    get_route_by_id as db_get_route_by_id,
    create_route as db_create_route,
    update_route as db_update_route,
    delete_route as db_delete_route,
)


def get_all_routes(status=None, page=1, per_page=10):
    """Get all routes with optional status filter."""
    return db_get_all_routes(status=status, page=page, per_page=per_page)


def count_routes(status=None):
    """Count total routes."""
    return db_count_routes(status=status)


def get_route_by_id(route_id: int):
    """Get route by ID."""
    return db_get_route_by_id(route_id)


def create_route_service(source_airport: str, destination_airport: str, distance_km: float, duration_minutes: int, status: str = "Active"):
    """Create a new route."""
    errors = []
    if not source_airport or not destination_airport:
        errors.append("Source and destination are required.")
    if source_airport == destination_airport:
        errors.append("Source and destination cannot be the same.")
    if not distance_km or distance_km <= 0:
        errors.append("Distance must be positive.")
    if not duration_minutes or duration_minutes <= 0:
        errors.append("Duration must be greater than zero.")

    if errors:
        raise ValueError(" ".join(errors))

    db_create_route(source_airport, destination_airport, distance_km, duration_minutes, status)


def update_route_service(route_id: int, source_airport: str, destination_airport: str, distance_km: float, duration_minutes: int, status: str):
    """Update an existing route."""
    errors = []
    if not source_airport or not destination_airport:
        errors.append("Source and destination are required.")
    if source_airport == destination_airport:
        errors.append("Source and destination cannot be the same.")
    if not distance_km or distance_km <= 0:
        errors.append("Distance must be positive.")
    if not duration_minutes or duration_minutes <= 0:
        errors.append("Duration must be greater than zero.")

    if errors:
        raise ValueError(" ".join(errors))

    db_update_route(route_id, source_airport, destination_airport, distance_km, duration_minutes, status)


def delete_route_service(route_id: int):
    """Delete a route."""
    db_delete_route(route_id)