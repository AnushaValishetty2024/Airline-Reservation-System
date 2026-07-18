"""New admin routes for Day 5 features."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from datetime import datetime


from services.admin_service import (
    get_admin_dashboard_kpis,
    get_all_bookings_admin,
    get_all_flights_admin,
    get_all_users_admin,
    get_booking_analytics,
    get_user_analytics,
    get_flight_analytics,
    get_route_analytics,
)
from services.dashboard_service import get_booking_details_enriched
from services.flight_service import toggle_flight_status_service
from services.user_service import toggle_user_status_service
from utils.pdf_generator import generate_ticket_pdf, generate_invoice_pdf
from services.revenue_analytics_service import get_revenue_analytics

admin_new_bp = Blueprint(
    'admin_new',
    __name__,
    url_prefix='/admin'
)


@admin_new_bp.route("/analytics/booking-trends")
def booking_trend_analysis():
    return render_template("analytics/booking_trends.html")

def admin_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(g, "current_user", None) or g.current_user["role_name"] != "Admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        return view(*args, **kwargs)

    return wrapped


# ==================== ADMIN DASHBOARD ====================

@admin_new_bp.route("/")
@admin_new_bp.route("/dashboard")
@admin_required
def dashboard():
    """Admin dashboard with KPIs."""
    kpis = get_admin_dashboard_kpis()
    return render_template(
        "admin/dashboard.html",
        page_title="Admin Dashboard",
        kpis=kpis,
    )


# ==================== ADMIN FLIGHTS ====================

@admin_new_bp.route("/admin/flights")
@admin_required
def flights():
    """Manage flights page."""
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort_by", "departure_datetime")
    sort_order = request.args.get("sort_order", "ASC")
    page = request.args.get("page", 1, type=int)
    
    flights_list, total, total_pages = get_all_flights_admin(
        search=search,
        status_filter=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=10
    )
    start_page = max(1, page - 2)
    end_page = min(total_pages + 1, page + 3)
    
    return render_template(
    "admin/flights.html",
    flights=flights_list,
    total=total,
    total_pages=total_pages,
    page=page,
    start_page=start_page,
    end_page=end_page
)


# ==================== ADMIN BOOKINGS ====================

@admin_new_bp.route("/admin/bookings")
@admin_required
def bookings():
    """Manage bookings page."""
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    sort_by = request.args.get("sort_by", "booked_at")
    sort_order = request.args.get("sort_order", "DESC")
    page = request.args.get("page", 1, type=int)
    
    bookings_list, total, total_pages = get_all_bookings_admin(
        search=search,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=10
    )
    start_page = max(1, page - 2)
    end_page = min(total_pages + 1, page + 3)
    return render_template(
    "admin/bookings.html",
    bookings=bookings_list,
    total=total,
    total_pages=total_pages,
    page=page,
    start_page=start_page,
    end_page=end_page
)

# ==================== ADMIN USERS ====================

@admin_new_bp.route("/admin/users")
@admin_required
def users():
    """Manage users page."""
    search = request.args.get("search", "")
    role_filter = request.args.get("role", "")
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "DESC")
    page = request.args.get("page", 1, type=int)
    
    users_list, total, total_pages = get_all_users_admin(
        search=search,
        role_filter=role_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=10
    )
    
    return render_template(
        "admin/users.html",
        page_title="Manage Users",
        users=users_list,
        search=search,
        role_filter=role_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        total_pages=total_pages,
        total=total,
    )


# ==================== ADMIN PAYMENTS ====================

@admin_new_bp.route("/admin/payments")
@admin_required
def payments():
    """Manage payments page."""
    # Get payment data
    from repositories.payment_repository import get_payment_report_summary
    report = get_payment_report_summary()
    
    # Get recent transactions
    from models.user import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                p.payment_reference,
                b.booking_reference,
                u.full_name AS passenger_name,
                p.amount,
                p.payment_method,
                ps.status_name AS payment_status,
                p.paid_at AS payment_date
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN users u ON b.user_id = u.id
            LEFT JOIN payment_status ps ON p.payment_status_id = ps.id
            ORDER BY p.paid_at DESC
            LIMIT 50
        """)
        recent_transactions = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    print(report)  
    
    return render_template(
        "admin/payments.html",
        page_title="Manage Payments",
        payment_report=report,
        recent_transactions=recent_transactions,
    )


# ==================== ADMIN REVENUE ====================

@admin_new_bp.route("/admin/revenue")
@admin_required
def revenue():
    """Revenue analytics page."""

    analytics = get_revenue_analytics()

    daily_revenue = analytics.get("daily_revenue", [])
    revenue_by_airline = analytics.get("revenue_by_airline", [])
    revenue_by_route = analytics.get("revenue_by_route", [])

    print("ANALYTICS:", analytics)

    return render_template(
        "admin/revenue.html",

        # KPI values
        total_revenue=analytics.get("total_revenue", 0),
        today_revenue=analytics.get("today_revenue", 0),
        weekly_revenue=analytics.get("weekly_revenue", 0),
        monthly_revenue=analytics.get("monthly_revenue", 0),
        yearly_revenue=analytics.get("yearly_revenue", 0),
        avg_ticket_price=analytics.get("avg_ticket_price", 0),

        # Charts
        daily_revenue=daily_revenue,
        revenue_by_airline=revenue_by_airline,
        revenue_by_route=revenue_by_route,

        # Complete data
        analytics_data=analytics
    )

# ==================== ADMIN ANALYTICS ====================

@admin_new_bp.route("/admin/analytics")
@admin_required
def analytics():
    print("🔥 ANALYTICS ROUTE RUNNING")

    analytics_data = get_revenue_analytics()

    print(analytics_data)

    return render_template(
        "admin/analytics.html",
        page_title="Analytics Dashboard",
        **analytics_data
    )

@admin_new_bp.route("/admin/analytics/bookings")
@admin_required
def analytics_bookings():
    """Booking analytics page."""
    analytics = get_booking_analytics()
    return render_template(
        "admin/analytics_bookings.html",
        page_title="Booking Analytics",
        analytics=analytics,
    )


@admin_new_bp.route("/admin/analytics/users")
@admin_required
def analytics_users():
    """User analytics page."""
    analytics = get_user_analytics()
    return render_template(
        "admin/analytics_users.html",
        page_title="User Analytics",
        analytics=analytics,
    )


@admin_new_bp.route("/admin/analytics/flights")
@admin_required
def analytics_flights():
    """Flight analytics page."""
    analytics = get_flight_analytics()
    return render_template(
        "admin/analytics_flights.html",
        page_title="Flight Analytics",
        analytics=analytics,
    )


@admin_new_bp.route("/admin/analytics/routes")
@admin_required
def analytics_routes():
    """Route analytics page."""
    analytics = get_route_analytics()
    return render_template(
        "admin/analytics_routes.html",
        page_title="Route Analytics",
        analytics=analytics,
    )


# ==================== TOGGLE HANDLERS ====================

@admin_new_bp.route("/admin/user/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active/inactive status."""
    try:
        toggle_user_status_service(user_id)
        flash("User status updated successfully.", "success")
    except Exception as e:
        flash(f"Failed to update user status: {str(e)}", "danger")
    return redirect(url_for("admin_new.users"))


@admin_new_bp.route("/admin/flight/<int:flight_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_flight_status(flight_id):
    """Toggle flight active/inactive status."""
    try:
        toggle_flight_status_service(flight_id)
        flash("Flight status updated successfully.", "success")
    except Exception as e:
        flash(f"Failed to update flight status: {str(e)}", "danger")
    return redirect(url_for("admin_new.flights"))


# ==================== DOWNLOAD HANDLERS ====================

@admin_new_bp.route("/admin/booking/<int:booking_id>/ticket")
@admin_required
def admin_download_ticket(booking_id):
    """Download ticket PDF (admin)."""
    booking = get_booking_details_enriched(booking_id, booking["user_id"])
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("admin_new.bookings"))
    
    try:
        pdf_path = generate_ticket_pdf(booking)
        return send_file(pdf_path, as_attachment=True, download_name=f"ticket_{booking['booking_reference']}.pdf")
    except Exception as e:
        flash(f"Failed to generate ticket: {str(e)}", "danger")
        return redirect(url_for("admin_new.bookings"))


@admin_new_bp.route("/admin/booking/<int:booking_id>/invoice")
@admin_required
def admin_download_invoice(booking_id):
    """Download invoice PDF (admin)."""
    booking = get_booking_details_enriched(booking_id, booking["user_id"])
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("admin_new.bookings"))
    
    try:
        pdf_path = generate_invoice_pdf(booking)
        return send_file(pdf_path, as_attachment=True, download_name=f"invoice_{booking['booking_reference']}.pdf")
    except Exception as e:
        flash(f"Failed to generate invoice: {str(e)}", "danger")
        return redirect(url_for("admin_new.bookings"))
    
@admin_new_bp.route('/revenue-analysis')
@admin_required
def revenue_analysis():

    data = get_revenue_analytics()

    for item in data.get("airline_revenue", []):
        item["revenue"] = float(item["revenue"])

    for item in data.get("monthly_revenue", []):
        item["revenue"] = float(item["revenue"])

    for item in data.get("route_revenue", []):
        item["revenue"] = float(item["revenue"])

    return render_template(
        "admin/revenue_analysis.html",
        data=data
    )

@admin_new_bp.route("/test-revenue")
def test_revenue():

    return "Revenue route is working"

@admin_new_bp.route("/business-analytics")
def business_analytics():
    return render_template("business_analytics.html")