from models.user import get_db_connection


class BusinessAnalyticsService:

    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def get_dashboard_kpis(self):
        """Return dashboard KPI values."""

        # Total Revenue
        self.cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total_revenue
            FROM payments
        """)
        revenue = self.cursor.fetchone()["total_revenue"]

        # Total Bookings
        self.cursor.execute("""
            SELECT COUNT(*) AS total_bookings
            FROM bookings
        """)
        bookings = self.cursor.fetchone()["total_bookings"]

        # Total Flights
        self.cursor.execute("""
            SELECT COUNT(*) AS total_flights
            FROM flights
        """)
        flights = self.cursor.fetchone()["total_flights"]

        # Total Customers
        self.cursor.execute("""
            SELECT COUNT(*) AS total_customers
            FROM users
            WHERE role_id = 2
        """)
        customers = self.cursor.fetchone()["total_customers"]

        # Occupancy Rate
        self.cursor.execute("""
            SELECT ROUND(
                (
                    SELECT COUNT(*)
                    FROM booking_passengers
                ) * 100.0 /
                (
                    SELECT SUM(seats_economy + seats_business)
                    FROM flights
                ),
                2
            ) AS occupancy_rate
        """)
        occupancy = self.cursor.fetchone()["occupancy_rate"] or 0

        # Cancellation Rate
        self.cursor.execute("""
            SELECT ROUND(
                (
                    SELECT COUNT(*)
                    FROM bookings
                    WHERE booking_status_id = (
                        SELECT id
                        FROM booking_status
                        WHERE LOWER(status_name) = 'cancelled'
                    )
                ) * 100.0 /
                COUNT(*),
                2
            ) AS cancellation_rate
            FROM bookings
        """)
        cancellation = self.cursor.fetchone()["cancellation_rate"] or 0

        return {
            "total_revenue": revenue,
            "total_bookings": bookings,
            "total_flights": flights,
            "total_customers": customers,
            "occupancy_rate": occupancy,
            "cancellation_rate": cancellation
        }

    def get_monthly_revenue(self):
        """Monthly revenue."""

        self.cursor.execute("""
            SELECT
                DATE_FORMAT(paid_at, '%b') AS month,
                SUM(amount) AS revenue
            FROM payments
            WHERE payment_status_id = 2
            GROUP BY YEAR(paid_at), MONTH(paid_at)
            ORDER BY YEAR(paid_at), MONTH(paid_at)
        """)

        return self.cursor.fetchall()

    def get_booking_trend(self):
        """Monthly booking trend."""

        self.cursor.execute("""
            SELECT
                DATE_FORMAT(booked_at, '%b') AS month,
                COUNT(*) AS bookings
            FROM bookings
            GROUP BY YEAR(booked_at), MONTH(booked_at)
            ORDER BY YEAR(booked_at), MONTH(booked_at)
        """)

        return self.cursor.fetchall()
    
    def get_revenue_by_airline(self):
        """Revenue grouped by airline."""

        self.cursor.execute("""
            SELECT
                 a.airline_name,
                 COALESCE(SUM(p.amount), 0) AS revenue
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            WHERE p.payment_status_id = 2
            GROUP BY a.airline_name
            ORDER BY revenue DESC
        """)

        return self.cursor.fetchall()
    def get_bookings_by_airline(self):
        """Bookings grouped by airline."""

        self.cursor.execute("""
            SELECT
                 a.airline_name,
                 COUNT(b.id) AS bookings
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            GROUP BY a.airline_name
            ORDER BY bookings DESC
        """)

        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()