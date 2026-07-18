from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, send_file
import os
from datetime import datetime

from services.user_service import get_all_users_service, update_user_profile as service_update_profile, change_password as service_change_password
from services.flight_service import get_airlines, get_airports, search_flights, get_aircraft
from services.booking_service import create_booking, get_booking_details, get_user_booking_history, get_booking_passengers_list, cancel_booking_service
from services.dashboard_service import (
    get_user_dashboard_kpis,
    get_booking_history,
    get_booking_details_enriched,
    get_upcoming_trips,
    get_user_analytics
)
from models.booking import get_booking_history_enriched
from utils.pdf_generator import generate_ticket_pdf, generate_invoice_pdf

user_bp = Blueprint("user", __name__)


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(g, "current_user", None):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@user_bp.route("/")
def home():
    return redirect(url_for("auth.login"))


@user_bp.route("/dashboard")
@login_required
def dashboard():

    print("USER DASHBOARD OPENED")
    print("CURRENT USER:", g.current_user)

    from services.booking_service import get_user_booking_history

    print(g.current_user)

      
    # Get KPI metrics
    kpis = get_user_dashboard_kpis(g.current_user["id"])
    
    # Get real booking data
    bookings = get_user_booking_history(g.current_user["id"])
    
    # Limit to 5 most recent for dashboard display
    recent_bookings = bookings[:5] if bookings else []
    
    # Calculate passenger counts for each booking
    booking_passenger_counts = {}
    for booking in recent_bookings:
        try:
            passengers = get_booking_passengers_list(booking["id"])
            booking_passenger_counts[booking["id"]] = len(passengers)
        except Exception:
            booking_passenger_counts[booking["id"]] = 0
    
    return render_template(
        "dashboard_new.html",
        page_title="Dashboard",
        recent_bookings=recent_bookings,
        booking_passenger_counts=booking_passenger_counts,
        kpis=kpis,
    )
@user_bp.route("/upcoming-trips")
@login_required
def upcoming_trips():

    trips = get_upcoming_trips(g.current_user["id"])

    return render_template(
        "upcoming_trips.html",
        page_title="Upcoming Trips",
        trips=trips
    )

@user_bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    airports = get_airports()
    airlines = get_airlines()

    passenger_count = 1

    flights = search_flights()

    if request.method == "POST":
        origin_id = request.form.get("origin_airport_id", type=int)
        destination_id = request.form.get("destination_airport_id", type=int)
        departure_date = request.form.get("departure_date", "")
        sort_by = request.form.get("sort_by", "departure_earliest")
        airline_id = request.form.get("airline_id", type=int)
        min_price = request.form.get("min_price", type=float)
        max_price = request.form.get("max_price", type=float)
        time_of_day = request.form.get("time_of_day", "")
        passenger_count = request.form.get("passenger_count", 1, type=int)

        flights = search_flights(
            origin_id=origin_id,
            destination_id=destination_id,
            departure_date=departure_date,
            sort_by=sort_by,
            airline_id=airline_id,
            min_price=min_price,
            max_price=max_price,
            time_of_day=time_of_day if time_of_day else None,
            passenger_count=passenger_count,
        )

    # ===== ADD THESE 4 LINES HERE =====
    print("\n===== SEARCH DEBUG =====")
    print("Method:", request.method)
    print("Form Passenger Count:", request.form.get("passenger_count"))
    print("Passenger Count Sent To Template:", passenger_count)
    # ==================================

    return render_template(
    "search_flights.html",
    page_title="Search Flights",
    flights=flights,
    airports=airports,
    airlines=airlines,
    passenger_count=passenger_count,
)
@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            mobile_number = request.form.get("mobile_number", "").strip()

            try:
                service_update_profile(g.current_user["id"], full_name, email, mobile_number)
                flash("Profile updated successfully.", "success")
                g.current_user = get_all_users_service()[0]  # Refresh user data
            except ValueError as e:
                flash(str(e), "danger")

        elif action == "change_password":
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
            else:
                try:
                    service_change_password(g.current_user["id"], new_password)
                    flash("Password changed successfully.", "success")
                except ValueError as e:
                    flash(str(e), "danger")

    return render_template("profile.html", page_title="Profile", users=get_all_users_service())


@user_bp.route("/book/<int:flight_id>", methods=["GET", "POST"])
@login_required
def book_flight(flight_id):
    from services.flight_service import get_flight_by_id

    flight = get_flight_by_id(flight_id)

    if not flight:
        flash("Flight not found.", "danger")
        return redirect(url_for("user.search"))

    # Default passenger count from URL (GET request)
    passenger_count = int(request.args.get("passenger_count", 1))

    print("\n=== BOOKING ROUTE DEBUG ===")
    print(f"Request Method: {request.method}")
    print(f"Request Args: {dict(request.args)}")
    print("Passenger Count From URL:", request.args.get("passenger_count"))
    print(f"Request Form: {dict(request.form)}")
    print(f"Request Form: {dict(request.form)}")
    print(f"Initial passenger_count: {passenger_count}")

    if request.method == "POST":

        print("\n=== FORM DATA ===")
        print(request.form.to_dict(flat=False))

        seat_class = request.form.get("seat_class", "economy")
        passenger_count = int(request.form.get("passenger_count", 1))

        print(f"POST passenger_count: {passenger_count}")

        # Calculate base price
        if seat_class.lower() == "economy":
            base_price = float(flight["economy_price"])
        else:
            base_price = float(flight["business_price"])

        # Gather all passengers
        passengers_data = []

        for i in range(passenger_count):
            passengers_data.append({
                "name": request.form.get(f"passenger_name_{i}", "").strip(),
                "email": request.form.get(f"passenger_email_{i}", "").strip(),
                "mobile": request.form.get(f"passenger_mobile_{i}", "").strip(),
                "passport": request.form.get(f"passenger_passport_{i}", "").strip(),
                "gender": request.form.get(f"passenger_gender_{i}", "").strip(),
                "dob": request.form.get(f"passenger_dob_{i}", "").strip(),
                "seat_number": request.form.get(f"seat_number_{i}", "").strip(),
            })

        total_amount = base_price * passenger_count

              # Debug
        print("\n=== PROCESSING BOOKING ===")
        print(f"Seat Class: {seat_class}")
        print(f"Base Price: {base_price}")
        print(f"Passenger Count: {passenger_count}")
        print(f"Total Amount: {total_amount}")

        for idx, passenger in enumerate(passengers_data, start=1):
            print(f"Passenger {idx}: {passenger}")

        try:
            booking_id = create_booking(
                user_id=g.current_user["id"],
                flight_id=flight_id,
                passengers_data=passengers_data,
                seat_class=seat_class,
                total_amount=total_amount,
            )

            flash(f"Booking created! Reference: {booking_id}", "success")
            return redirect(url_for("payment.payment_page", booking_id=booking_id))

        except Exception as e:
            flash(f"Booking failed: {str(e)}", "danger")

    print("\n=== RENDER BOOKING PAGE ===")
    print(f"Passenger Count: {passenger_count}")
    print(f"Economy Seats: {flight.get('seats_economy')}")
    print(f"Business Seats: {flight.get('seats_business')}")

    return render_template(
        "book_flight.html",
        page_title="Confirm Booking",
        flight=flight,
        passenger_count=passenger_count,
    )
@login_required
def api_booking_details(booking_id):
    """JSON API endpoint for booking details."""
    from services.booking_service import get_booking_details, get_booking_passengers_list
    
    try:
        booking = get_booking_details(booking_id)
        passengers = get_booking_passengers_list(booking_id)
        
        # Ensure user can only access their own bookings
        if booking["user_id"] != g.current_user["id"]:
            return {"error": "Access denied."}, 403
        
        return {
            "booking": booking,
            "passengers": passengers
        }
    except ValueError as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": str(e)}, 500


@user_bp.route("/api/bookings")
@login_required
def api_user_bookings():
    """JSON API endpoint for user booking history."""
    from services.booking_service import get_user_booking_history
    
    bookings = get_user_booking_history(g.current_user["id"])
    return {"bookings": bookings}


@user_bp.route("/history")
@login_required
def booking_history():
    # Get filter parameters
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    sort_by = request.args.get("sort_by", "booked_at")
    sort_order = request.args.get("sort_order", "DESC")
    page = request.args.get("page", 1, type=int)
    
    # Get paginated bookings with filters
    bookings, total, total_pages = get_booking_history(
        user_id=g.current_user["id"],
        search=search,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=10
    )
    
    # Fetch passengers for each booking
    booking_passengers = {}
    for booking in bookings:
        try:
            passengers = get_booking_passengers_list(booking["id"])
            booking_passengers[booking["id"]] = passengers
        except Exception:
            booking_passengers[booking["id"]] = []

    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    
    return render_template(
        "booking_history.html",
        page_title="Booking History",
        bookings=bookings,
        booking_passengers=booking_passengers,
        search=search,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        total_pages=total_pages,
        total=total,
        start_page=start_page,
        end_page=end_page,
)



@user_bp.route("/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking_route(booking_id):
    try:
        cancel_booking_service(booking_id, g.current_user["id"])
        flash("Booking cancelled successfully.", "success")
    except Exception as e:
        flash(f"Cancel failed: {str(e)}", "danger")
    return redirect(url_for("user.booking_history"))




@user_bp.route("/analytics")
@login_required
def travel_analytics():
    """Display travel analytics for the user."""
    analytics = get_user_analytics(g.current_user["id"])
    print("========== ANALYTICS ==========")
    print(type(analytics))
    print(analytics)
    print("===============================")
    print("Analytics type:", type(analytics))
    print("Analytics keys:", analytics.keys())
    print("Analytics:", analytics)
    return render_template(
        "travel_analytics.html",
        page_title="Travel Analytics",
        analytics=analytics,
    )


@user_bp.route("/dashboard/analytics")
@login_required
def dashboard_analytics():
    """Display comprehensive analytics for user dashboard."""
    analytics = get_user_analytics(g.current_user["id"])
    return render_template(
        "travel_analytics.html",
        page_title="My Travel Analytics",
        analytics=analytics,
    )


@user_bp.route("/booking/<int:booking_id>/ticket")
@login_required
def download_ticket(booking_id):
    """Download ticket PDF."""
    booking = get_booking_details_enriched(booking_id, g.current_user["id"])
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("user.booking_history"))
    
    try:
        pdf_path = generate_ticket_pdf(booking)
        return send_file(pdf_path, as_attachment=True, download_name=f"ticket_{booking['booking_reference']}.pdf")
    except Exception as e:
        flash(f"Failed to generate ticket: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))


@user_bp.route("/booking/<int:booking_id>/boarding-pass")
@login_required
def download_boarding_pass(booking_id):
    """Download boarding pass PDF."""
    booking = get_booking_details_enriched(booking_id, g.current_user["id"])
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("user.booking_history"))
    
    try:
        pdf_path = generate_ticket_pdf(booking)  # Reuse ticket generator for boarding pass
        return send_file(pdf_path, as_attachment=True, download_name=f"boarding_pass_{booking['booking_reference']}.pdf")
    except Exception as e:
        flash(f"Failed to generate boarding pass: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))


@user_bp.route("/booking/<int:booking_id>/invoice")
@login_required
def download_invoice(booking_id):
    """Download invoice PDF."""
    booking = get_booking_details_enriched(booking_id, g.current_user["id"])
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("user.booking_history"))
    
    try:
        pdf_path = generate_invoice_pdf(booking)
        return send_file(pdf_path, as_attachment=True, download_name=f"invoice_{booking['booking_reference']}.pdf")
    except Exception as e:
        flash(f"Failed to generate invoice: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))
