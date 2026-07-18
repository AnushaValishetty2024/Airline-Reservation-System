from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from services.airline_service import (
    count_airlines, create_airline, delete_airline, get_all_airlines, get_airline_by_code, get_airline_by_id, toggle_airline_status, update_airline,
)
from services.flight_service import (
    create_flight_service, delete_flight_service, get_aircraft, get_airlines, get_airports, get_all_flights, update_flight_service,
)
from services.route_service import (
    count_routes, create_route_service, delete_route_service, get_all_routes, get_route_by_id, update_route_service,
)
from services.schedule_service import (
    count_schedules, create_schedule_service, delete_schedule_service, get_all_schedules, get_schedule_by_id, get_schedules_by_flight, update_schedule_service,
)
from services.user_service import get_all_users_service
from services.payment_service import get_payment_report_summary

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(g, "current_user", None) or g.current_user["role_name"] != "Admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    
    print("===== ADMIN DASHBOARD =====")

    users = get_all_users_service()
    return render_template(
        "dashboard.html",
        page_title="Admin Dashboard",
        users=users,
        user_count=len(users),
        show_admin_metrics=True,
    )


@admin_bp.route("/admin/airlines", methods=["GET", "POST"])
@admin_required
def airlines():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            airline_name = request.form.get("airline_name", "").strip()
            airline_code = request.form.get("airline_code", "").strip().upper()
            country = request.form.get("country", "").strip()
            status = request.form.get("status", "Active")

            if not airline_name or not airline_code or not country:
                flash("All fields are required.", "danger")
            else:
                try:
                    create_airline(airline_name, airline_code, country, status)
                    flash("Airline added successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

        elif action == "edit":
            airline_id = request.form.get("airline_id", type=int)
            airline_name = request.form.get("airline_name", "").strip()
            airline_code = request.form.get("airline_code", "").strip().upper()
            country = request.form.get("country", "").strip()
            status = request.form.get("status", "Active")

            if not airline_name or not airline_code or not country:
                flash("All fields are required.", "danger")
            else:
                try:
                    update_airline(airline_id, airline_name, airline_code, country, status)
                    flash("Airline updated successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

        elif action == "delete":
            airline_id = request.form.get("airline_id", type=int)
            try:
                delete_airline(airline_id)
                flash("Airline deleted successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")

        elif action == "toggle_status":
            airline_id = request.form.get("airline_id", type=int)
            try:
                new_status = toggle_airline_status(airline_id)
                flash(f"Airline {new_status.lower()}d successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")

    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")
    per_page = 10

    airlines_list = get_all_airlines(status=status_filter or None, page=page, per_page=per_page)
    total = count_airlines(status=status_filter or None)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "admin_airlines.html",
        page_title="Manage Airlines",
        airlines=airlines_list,
        page=page,
        total_pages=total_pages,
        status_filter=status_filter,
    )


@admin_bp.route("/admin/routes", methods=["GET", "POST"])
@admin_required
def routes():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            source = request.form.get("source_airport", "").strip()
            destination = request.form.get("destination_airport", "").strip()
            distance = request.form.get("distance_km", type=float)
            duration = request.form.get("duration_minutes", type=int)
            status = request.form.get("status", "Active")

            errors = []
            if not source or not destination:
                errors.append("Source and destination are required.")
            if source == destination:
                errors.append("Source and destination cannot be the same.")
            if not distance or distance <= 0:
                errors.append("Distance must be positive.")
            if not duration or duration <= 0:
                errors.append("Duration must be greater than zero.")

            if errors:
                for error in errors:
                    flash(error, "danger")
            else:
                try:
                    create_route_service(source, destination, distance, duration, status)
                    flash("Route added successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

        elif action == "edit":
            route_id = request.form.get("route_id", type=int)
            source = request.form.get("source_airport", "").strip()
            destination = request.form.get("destination_airport", "").strip()
            distance = request.form.get("distance_km", type=float)
            duration = request.form.get("duration_minutes", type=int)
            status = request.form.get("status", "Active")

            errors = []
            if not source or not destination:
                errors.append("Source and destination are required.")
            if source == destination:
                errors.append("Source and destination cannot be the same.")
            if not distance or distance <= 0:
                errors.append("Distance must be positive.")
            if not duration or duration <= 0:
                errors.append("Duration must be greater than zero.")

            if errors:
                for error in errors:
                    flash(error, "danger")
            else:
                try:
                    update_route_service(route_id, source, destination, distance, duration, status)
                    flash("Route updated successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

        elif action == "delete":
            route_id = request.form.get("route_id", type=int)
            try:
                delete_route_service(route_id)
                flash("Route deleted successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")

    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")
    per_page = 10

    routes_list = get_all_routes(status=status_filter or None, page=page, per_page=per_page)
    total = count_routes(status=status_filter or None)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "admin_routes.html",
        page_title="Manage Routes",
        routes=routes_list,
        page=page,
        total_pages=total_pages,
        status_filter=status_filter,
    )


@admin_bp.route("/admin/schedules", methods=["GET", "POST"])
@admin_required
def schedules():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            flight_id = request.form.get("flight_id", type=int)
            departure_time = request.form.get("departure_time", "")
            arrival_time = request.form.get("arrival_time", "")
            price = request.form.get("price", type=float)
            terminal = request.form.get("terminal", "").strip()
            gate_number = request.form.get("gate_number", "").strip()
            status = request.form.get("status", "Scheduled")

            errors = []
            if not flight_id:
                errors.append("Flight is required.")
            if not departure_time or not arrival_time:
                errors.append("Departure and arrival times are required.")
            if departure_time and arrival_time and arrival_time <= departure_time:
                errors.append("Arrival time must be after departure time.")
            if not price or price <= 0:
                errors.append("Price must be greater than zero.")

            if errors:
                for error in errors:
                    flash(error, "danger")
            else:
                try:
                    create_schedule_service(flight_id, departure_time, arrival_time, price, terminal or None, gate_number or None, status)
                    flash("Schedule added successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

        elif action == "edit":
            schedule_id = request.form.get("schedule_id", type=int)
            flight_id = request.form.get("flight_id", type=int)
            departure_time = request.form.get("departure_time", "")
            arrival_time = request.form.get("arrival_time", "")
            price = request.form.get("price", type=float)
            terminal = request.form.get("terminal", "").strip()
            gate_number = request.form.get("gate_number", "").strip()
            status = request.form.get("status", "Scheduled")

            errors = []
            if not flight_id:
                errors.append("Flight is required.")
            if not departure_time or not arrival_time:
                errors.append("Departure and arrival times are required.")
            if departure_time and arrival_time and arrival_time <= departure_time:
                errors.append("Arrival time must be after departure time.")
            if not price or price <= 0:
                errors.append("Price must be greater than zero.")

            if errors:
                for error in errors:
                    flash(error, "danger")
            else:
                try:
                    update_schedule_service(schedule_id, flight_id, departure_time, arrival_time, price, terminal or None, gate_number or None, status)
                    flash("Schedule updated successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

        elif action == "delete":
            schedule_id = request.form.get("schedule_id", type=int)
            try:
                delete_schedule_service(schedule_id)
                flash("Schedule deleted successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")

    schedules_list = get_all_schedules()
    return render_template(
        "admin_schedules.html",
        page_title="Manage Schedules",
        schedules=schedules_list,
        flights=get_all_flights(),
    )


@admin_bp.route("/admin/flights", methods=["GET", "POST"])
@admin_required
def flights():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            try:
                create_flight_service(
                    request.form.get("flight_number", ""),
                    request.form.get("airline_id", type=int),
                    request.form.get("aircraft_id", type=int),
                    request.form.get("origin_airport_id", type=int),
                    request.form.get("destination_airport_id", type=int),
                    request.form.get("departure_datetime", ""),
                    request.form.get("arrival_datetime", ""),
                    request.form.get("economy_price", type=float),
                    request.form.get("business_price", type=float),
                    request.form.get("status", "Scheduled"),
                )
                flash("Flight created successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")
        elif action == "edit":
            try:
                update_flight_service(
                    request.form.get("flight_id", type=int),
                    request.form.get("flight_number", ""),
                    request.form.get("airline_id", type=int),
                    request.form.get("aircraft_id", type=int),
                    request.form.get("origin_airport_id", type=int),
                    request.form.get("destination_airport_id", type=int),
                    request.form.get("departure_datetime", ""),
                    request.form.get("arrival_datetime", ""),
                    request.form.get("economy_price", type=float),
                    request.form.get("business_price", type=float),
                    request.form.get("status", "Scheduled"),
                )
                flash("Flight updated successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")
        elif action == "delete":
            try:
                delete_flight_service(request.form.get("flight_id", type=int))
                flash("Flight deleted successfully.", "success")
            except ValueError as e:
                flash(str(e), "danger")

    flights_list = get_all_flights()
    return render_template(
        "admin_flights.html",
        page_title="Manage Flights",
        flights=flights_list,
        airlines=get_airlines(),
        airports=get_airports(),
        aircraft=get_aircraft(),
    )


@admin_bp.route("/admin/users")
@admin_required
def users():
    return render_template("dashboard.html", page_title="Manage Users", users=get_all_users_service())


@admin_bp.route("/admin/reports")
@admin_required
def reports():
    return render_template("dashboard.html", page_title="View Reports")


@admin_bp.route("/admin/payments")
@admin_required
def payments():

    print("===== PAYMENT DASHBOARD =====")
    """Admin payment dashboard with analytics."""
    from models.user import get_db_connection
    
    # Get payment report summary
    report = get_payment_report_summary()
    
    # Get recent transactions
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                p.payment_reference,
                b.booking_reference,
                CONCAT(pax.full_name) AS passenger_name,
                p.amount,
                p.payment_method,
                ps.status_name AS payment_status,
                p.paid_at AS payment_date
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            LEFT JOIN booking_passengers bp ON bp.booking_id = b.id
            LEFT JOIN passengers pax ON pax.id = bp.passenger_id
            LEFT JOIN payment_status ps ON p.payment_status_id = ps.id
            ORDER BY p.paid_at DESC
            LIMIT 50
        """)
        recent_transactions = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    
    return render_template(
        "dashboard.html",
        page_title="Payment Dashboard",
        payment_report=report,
        recent_transactions=recent_transactions,
        show_payment_dashboard=True,
    )


@admin_bp.route("/admin/bookings")
@admin_required
def bookings():
    return render_template("dashboard.html", page_title="View All Bookings")