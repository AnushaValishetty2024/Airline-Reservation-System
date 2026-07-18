from flask import Blueprint, render_template

from services.sql_report_service import (
    get_revenue_report,
    get_booking_report,
    get_customer_report,
    get_flight_report,
    get_route_report
)


reports = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports.route("/")
def dashboard():

    revenue = get_revenue_report()
    bookings = get_booking_report()
    customers = get_customer_report()
    flights = get_flight_report()
    routes = get_route_report()


    return render_template(
    "analytics/reports_dashboard.html",
    revenue=revenue,
    bookings=bookings,
    customers=customers,
    flights=flights,
    routes=routes
)