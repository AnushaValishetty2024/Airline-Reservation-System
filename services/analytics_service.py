"""Advanced Analytics service for the airline reservation system."""
from mysql.connector import Error
from models.user import get_db_connection


class AnalyticsService:
    """Service for generating comprehensive analytics and reports."""

    def get_dashboard_kpis(self) -> dict:
        """Get key performance indicators for the analytics dashboard."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            kpis = {}
            
            # Total Revenue
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) AS total_revenue
                FROM payments
                WHERE payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            """)
            kpis["total_revenue"] = cursor.fetchone()["total_revenue"]
            
            # Total Bookings
            cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
            kpis["total_bookings"] = cursor.fetchone()["total_bookings"]
            
            # Total Flights
            cursor.execute("SELECT COUNT(*) AS total_flights FROM flights")
            kpis["total_flights"] = cursor.fetchone()["total_flights"]
            
            # Total Airlines
            cursor.execute("SELECT COUNT(*) AS total_airlines FROM airlines WHERE is_active = 1")
            kpis["total_airlines"] = cursor.fetchone()["total_airlines"]
            
            # Total Customers
            cursor.execute("SELECT COUNT(*) AS total_customers FROM users WHERE is_active = 1")
            kpis["total_customers"] = cursor.fetchone()["total_customers"]
            
            # Today's Revenue
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) AS today_revenue
                FROM payments
                WHERE DATE(paid_at) = CURDATE()
                AND payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            """)
            kpis["today_revenue"] = cursor.fetchone()["today_revenue"]
            
            # Today's Bookings
            cursor.execute("""
                SELECT COUNT(*) AS today_bookings
                FROM bookings
                WHERE DATE(booked_at) = CURDATE()
            """)
            kpis["today_bookings"] = cursor.fetchone()["today_bookings"]
            
            # Average Booking Value
            cursor.execute("""
                SELECT COALESCE(AVG(amount), 0) AS avg_booking_value
                FROM payments
                WHERE payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            """)
            kpis["avg_booking_value"] = cursor.fetchone()["avg_booking_value"]
            
            # Occupancy Rate
            cursor.execute("""
                SELECT COALESCE(AVG(occupancy_rate), 0) AS avg_occupancy
                FROM vw_flight_performance
            """)
            kpis["avg_occupancy"] = cursor.fetchone()["avg_occupancy"]
            
            return kpis
        
        finally:
            cursor.close()
            conn.close()

    def get_revenue_trends(self, days: int = 30) -> list:
        """Get daily revenue trends for the specified number of days."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT DATE(paid_at) AS date, SUM(amount) AS revenue
                FROM payments
                WHERE paid_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
                GROUP BY DATE(paid_at)
                ORDER BY date ASC
            """, (days,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_monthly_revenue(self, months: int = 12) -> list:
        """Get monthly revenue for the specified number of months."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT DATE_FORMAT(paid_at, '%Y-%m') AS month, SUM(amount) AS revenue
                FROM payments
                WHERE paid_at >= DATE_SUB(NOW(), INTERVAL %s MONTH)
                AND payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
                GROUP BY DATE_FORMAT(paid_at, '%Y-%m')
                ORDER BY month ASC
            """, (months,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_booking_trends(self, months: int = 12) -> list:
        """Get monthly booking trends."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT DATE_FORMAT(booked_at, '%Y-%m') AS month, COUNT(*) AS bookings
                FROM bookings
                WHERE booked_at >= DATE_SUB(NOW(), INTERVAL %s MONTH)
                GROUP BY DATE_FORMAT(booked_at, '%Y-%m')
                ORDER BY month ASC
            """, (months,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_booking_status_distribution(self) -> dict:
        """Get booking status distribution."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT bs.status_name, COUNT(b.id) AS count
                FROM bookings b
                JOIN booking_status bs ON b.booking_status_id = bs.id
                GROUP BY bs.status_name
            """)
            return {row["status_name"]: row["count"] for row in cursor.fetchall()}
        
        finally:
            cursor.close()
            conn.close()

    def get_top_airlines_by_revenue(self, limit: int = 10) -> list:
        """Get top airlines by revenue."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT airline_name, airline_code, total_bookings, total_revenue, avg_ticket_price
                FROM vw_revenue_summary
                ORDER BY total_revenue DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_top_routes_by_bookings(self, limit: int = 10) -> list:
        """Get top routes by bookings."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT route_name, origin_city, destination_city, total_bookings, total_revenue, occupancy_rate
                FROM vw_route_performance
                ORDER BY total_bookings DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_top_flights_by_occupancy(self, limit: int = 10) -> list:
        """Get top flights by occupancy rate."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT flight_number, airline_name, aircraft_model, total_capacity, 
                       confirmed_bookings, occupancy_rate, total_revenue
                FROM vw_flight_performance
                ORDER BY occupancy_rate DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_customer_insights(self, limit: int = 10) -> list:
        """Get top customers by spending."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT full_name, email, total_bookings, total_spent, avg_booking_value
                FROM vw_customer_summary
                WHERE total_bookings > 0
                ORDER BY total_spent DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_payment_method_distribution(self) -> dict:
        """Get payment method distribution."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT payment_method, COUNT(*) AS count, SUM(amount) AS total_amount
                FROM payments
                WHERE payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
                GROUP BY payment_method
            """)
            return {row["payment_method"]: row["count"] for row in cursor.fetchall()}
        
        finally:
            cursor.close()
            conn.close()

    def get_airline_distribution(self) -> dict:
        """Get airline distribution by bookings."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT a.airline_name, COUNT(DISTINCT b.id) AS bookings
                FROM bookings b
                JOIN flights f ON b.flight_id = f.id
                JOIN airlines a ON f.airline_id = a.id
                JOIN booking_status bs ON b.booking_status_id = bs.id
                WHERE bs.status_name != 'Cancelled'
                GROUP BY a.airline_name
                ORDER BY bookings DESC
            """)
            return {row["airline_name"]: row["bookings"] for row in cursor.fetchall()}
        
        finally:
            cursor.close()
            conn.close()

    def get_weekly_revenue(self, weeks: int = 12) -> list:
        """Get weekly revenue trends."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT YEARWEEK(paid_at) AS week, SUM(amount) AS revenue
                FROM payments
                WHERE paid_at >= DATE_SUB(NOW(), INTERVAL %s WEEK)
                AND payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
                GROUP BY YEARWEEK(paid_at)
                ORDER BY week ASC
            """, (weeks,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_hourly_booking_distribution(self) -> list:
        """Get hourly booking distribution."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT HOUR(booked_at) AS hour, COUNT(*) AS bookings
                FROM bookings
                GROUP BY HOUR(booked_at)
                ORDER BY hour ASC
            """)
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_aircraft_utilization(self) -> list:
        """Get aircraft utilization stats."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT ac.aircraft_model, COUNT(DISTINCT f.id) AS total_flights,
                       SUM(fp.total_bookings) AS total_bookings,
                       AVG(fp.occupancy_rate) AS avg_occupancy
                FROM aircraft ac
                JOIN flights f ON ac.id = f.aircraft_id
                JOIN vw_flight_performance fp ON f.id = fp.id
                GROUP BY ac.aircraft_model
                ORDER BY avg_occupancy DESC
            """)
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()

    def get_revenue_by_payment_method(self, months: int = 6) -> list:
        """Get revenue breakdown by payment method."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT payment_method, DATE_FORMAT(paid_at, '%Y-%m') AS month, SUM(amount) AS revenue
                FROM payments
                WHERE paid_at >= DATE_SUB(NOW(), INTERVAL %s MONTH)
                AND payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
                GROUP BY payment_method, DATE_FORMAT(paid_at, '%Y-%m')
                ORDER BY month ASC, payment_method ASC
            """, (months,))
            return cursor.fetchall()
        
        finally:
            cursor.close()
            conn.close()


# Singleton instance
analytics_service = AnalyticsService()