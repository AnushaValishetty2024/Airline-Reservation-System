from flask import Blueprint, render_template
from services.business_analytics_service import BusinessAnalyticsService
from services.booking_analytics_service import get_booking_trend_analytics
from services.occupancy_service import OccupancyService
from services.customer_analytics_service import CustomerAnalyticsService

from services.cancellation_service import (
    get_cancellation_metrics,
    get_cancelled_routes,
    get_monthly_cancellation_trend
)

from services.flight_analytics_service import (
    get_best_routes,
    get_highest_revenue_flights,
    get_most_booked_flights
)

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/admin/analytics"
)


@analytics_bp.route("/")
def dashboard():

    service = BusinessAnalyticsService()

    analytics = service.get_dashboard_kpis()
    monthly_revenue = service.get_monthly_revenue()
    booking_trend = service.get_booking_trend()
    revenue_by_airline = service.get_revenue_by_airline()
    bookings_by_airline = service.get_bookings_by_airline()

    service.close()

    return render_template(
        "admin/analytics_dashboard.html",
        analytics=analytics,
        monthly_revenue=monthly_revenue,
        booking_trend=booking_trend,
        revenue_by_airline=revenue_by_airline,
        bookings_by_airline=bookings_by_airline
    )


@analytics_bp.route("/booking-trends")
def booking_trends():

    data = get_booking_trend_analytics()

    return render_template(
        "analytics/booking_trends.html",
        booking_data=data
    )

@analytics_bp.route("/occupancy")
def occupancy():

    service = OccupancyService()

    occupancy_data = service.get_occupancy_data()


    most_occupied = sorted(
        occupancy_data,
        key=lambda x:x["occupancy"],
        reverse=True
    )[:5]


    low_occupied = sorted(
        occupancy_data,
        key=lambda x:x["occupancy"]
    )[:5]


    return render_template(
        "admin/analytics_occupancy.html",

        occupancy_data=occupancy_data,

        most_occupied=most_occupied,

        low_occupied=low_occupied
    )

@analytics_bp.route("/cancellation")
def cancellation():

    metrics = get_cancellation_metrics()

    routes = get_cancelled_routes()

    monthly = get_monthly_cancellation_trend()

    print("Monthly Cancellation Data:", monthly)


    return render_template(
        "analytics/cancellation.html",
        metrics=metrics,
        routes=routes,
        monthly=monthly
    )
@analytics_bp.route("/customers")
def customer_analytics():


    service = CustomerAnalyticsService()


    data={

        "total_customers":
        service.get_total_customers(),


        "active_customers":
        service.get_active_customers(),


        "top_customers":
        service.get_top_customers(),


        "booking_frequency":
        service.get_booking_frequency(),


        "customer_spending":
        service.get_customer_spending()

    }


    return render_template(
        "analytics/customer_analytics.html",
        data=data
    )
@analytics_bp.route('/flight-performance')
def flight_performance():

    routes = get_best_routes()

    revenue_flights = get_highest_revenue_flights()

    booked_flights = get_most_booked_flights()

    return render_template(
        "analytics/flight_performance.html",
        routes=routes,
        revenue_flights=revenue_flights,
        booked_flights=booked_flights
    )
