"""Admin service for managing flights, bookings, users, and payments."""
from mysql.connector import Error
from models.user import get_db_connection
from datetime import datetime


def get_admin_dashboard_kpis() -> dict:
    """Get KPI metrics for admin dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        kpis = {}
        
        # Total Users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE is_active = 1")
        kpis["total_users"] = cursor.fetchone()["total_users"]
        
        # Total Flights
        cursor.execute("SELECT COUNT(*) AS total_flights FROM flights")
        kpis["total_flights"] = cursor.fetchone()["total_flights"]
        
        # Total Bookings
        cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
        kpis["total_bookings"] = cursor.fetchone()["total_bookings"]
        
        # Today's Bookings
        cursor.execute("""
            SELECT COUNT(*) AS today_bookings 
            FROM bookings 
            WHERE DATE(booked_at) = CURDATE()
        """)
        kpis["today_bookings"] = cursor.fetchone()["today_bookings"]
        
        # Booking Status Counts
        cursor.execute("""
            SELECT bs.status_name, COUNT(b.id) AS count
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            GROUP BY bs.status_name
        """)
        status_counts = {row["status_name"]: row["count"] for row in cursor.fetchall()}
        kpis["confirmed_bookings"] = status_counts.get("Confirmed", 0)
        kpis["cancelled_bookings"] = status_counts.get("Cancelled", 0)
        kpis["completed_bookings"] = status_counts.get("Completed", 0)
        kpis["pending_bookings"] = status_counts.get("Pending", 0)
        
        # Today's Revenue
        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) AS today_revenue
            FROM payments p
            WHERE DATE(p.paid_at) = CURDATE()
            AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
        """)
        kpis["today_revenue"] = cursor.fetchone()["today_revenue"] or 0.0
        
        # Monthly Revenue
        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) AS monthly_revenue
            FROM payments p
            WHERE MONTH(p.paid_at) = MONTH(CURDATE())
            AND YEAR(p.paid_at) = YEAR(CURDATE())
            AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
        """)
        kpis["monthly_revenue"] = cursor.fetchone()["monthly_revenue"] or 0.0
        
        # Yearly Revenue
        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) AS yearly_revenue
            FROM payments p
            WHERE YEAR(p.paid_at) = YEAR(CURDATE())
            AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
        """)
        kpis["yearly_revenue"] = cursor.fetchone()["yearly_revenue"] or 0.0
        
        # Average Ticket Price
        cursor.execute("""
            SELECT COALESCE(AVG(p.amount), 0) AS avg_ticket_price
            FROM payments p
            WHERE p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
        """)
        kpis["avg_ticket_price"] = cursor.fetchone()["avg_ticket_price"] or 0.0
        
        return kpis
    
    finally:
        cursor.close()
        conn.close()


def get_all_bookings_admin(search: str = "", status_filter: str = "",
                           date_from: str = "", date_to: str = "",
                           sort_by: str = "booked_at", sort_order: str = "DESC",
                           page: int = 1, per_page: int = 10) -> tuple:
    """Get all bookings with filters for admin."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(b.booking_reference LIKE %s OR f.flight_number LIKE %s OR u.full_name LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        if status_filter:
            where_clauses.append("bs.status_name = %s")
            params.append(status_filter)
        
        if date_from:
            where_clauses.append("DATE(b.booked_at) >= %s")
            params.append(date_from)
        
        if date_to:
            where_clauses.append("DATE(b.booked_at) <= %s")
            params.append(date_to)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Validate sort
        allowed_sort = ["booked_at", "total_amount", "flight_number", "booking_status", "full_name"]
        if sort_by not in allowed_sort:
            sort_by = "booked_at"
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "DESC"
        
        # Count total
        cursor.execute(f"""
            SELECT COUNT(DISTINCT b.id) AS total
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN booking_status bs ON b.booking_status_id = bs.id
            JOIN flights f ON b.flight_id = f.id
            WHERE {where_sql}
        """, params)
        total = cursor.fetchone()["total"]
        
        offset = (page - 1) * per_page
        
        # Get bookings
        cursor.execute(f"""
            SELECT 
                b.id, b.booking_reference, b.total_amount, b.booked_at,
                bs.status_name AS booking_status,
                f.flight_number,
                u.full_name AS user_name,
                u.email AS user_email,
                COUNT(bp.id) AS passenger_count
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN booking_status bs ON b.booking_status_id = bs.id
            JOIN flights f ON b.flight_id = f.id
            LEFT JOIN booking_passengers bp ON bp.booking_id = b.id
            WHERE {where_sql}
            GROUP BY b.id, b.booking_reference, b.total_amount, b.booked_at,
                     bs.status_name, f.flight_number, u.full_name, u.email
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        bookings = cursor.fetchall()
        total_pages = (total + per_page - 1) // per_page
        
        return bookings, total, total_pages
    
    finally:
        cursor.close()
        conn.close()


def get_all_flights_admin(search: str = "", status_filter: str = "",
                          sort_by: str = "departure_datetime", sort_order: str = "ASC",
                          page: int = 1, per_page: int = 10) -> tuple:
    """Get all flights with filters for admin."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(f.flight_number LIKE %s OR a.airline_name LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if status_filter:
            where_clauses.append("f.status = %s")
            params.append(status_filter)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Validate sort
        allowed_sort = ["departure_datetime", "flight_number", "economy_price", "status"]
        if sort_by not in allowed_sort:
            sort_by = "departure_datetime"
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "ASC"
        
        # Count total
        cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM flights f
            JOIN airlines a ON f.airline_id = a.id
            WHERE {where_sql}
        """, params)
        total = cursor.fetchone()["total"]
        
        offset = (page - 1) * per_page
        
        # Get flights
        cursor.execute(f"""
            SELECT 
                f.id, f.flight_number, f.departure_datetime, f.arrival_datetime,
                f.economy_price, f.business_price, f.seats_economy, f.seats_business, f.status,
                a.airline_name,
                ap1.airport_code AS origin_code, ap1.city AS origin_city,
                ap2.airport_code AS destination_code, ap2.city AS destination_city,
                ac.aircraft_model
            FROM flights f
            JOIN airlines a ON f.airline_id = a.id
            JOIN airports ap1 ON f.origin_airport_id = ap1.id
            JOIN airports ap2 ON f.destination_airport_id = ap2.id
            JOIN aircraft ac ON f.aircraft_id = ac.id
            WHERE {where_sql}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        flights = cursor.fetchall()
        total_pages = (total + per_page - 1) // per_page
        
        return flights, total, total_pages
    
    finally:
        cursor.close()
        conn.close()


def get_all_users_admin(search: str = "", role_filter: str = "",
                        sort_by: str = "created_at", sort_order: str = "DESC",
                        page: int = 1, per_page: int = 10) -> tuple:
    """Get all users with filters for admin."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(u.full_name LIKE %s OR u.email LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if role_filter:
            where_clauses.append("r.role_name = %s")
            params.append(role_filter)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Validate sort
        allowed_sort = ["created_at", "full_name", "email", "role_name"]
        if sort_by not in allowed_sort:
            sort_by = "created_at"
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "DESC"
        
        # Count total
        cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM users u
            JOIN user_roles r ON u.role_id = r.id
            WHERE {where_sql}
        """, params)
        total = cursor.fetchone()["total"]
        
        offset = (page - 1) * per_page
        
        # Get users
        cursor.execute(f"""
            SELECT 
                u.id, u.full_name, u.email, u.mobile_number, u.is_active,
                u.created_at, u.updated_at,
                r.role_name,
                COUNT(DISTINCT b.id) AS total_bookings,
                COALESCE(SUM(p.amount), 0) AS total_spent
            FROM users u
            JOIN user_roles r ON u.role_id = r.id
            LEFT JOIN bookings b ON b.user_id = u.id
            LEFT JOIN payments p ON p.booking_id = b.id
                AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            WHERE {where_sql}
            GROUP BY u.id, u.full_name, u.email, u.mobile_number, u.is_active,
                     u.created_at, u.updated_at, r.role_name
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        users = cursor.fetchall()
        total_pages = (total + per_page - 1) // per_page
        
        return users, total, total_pages
    
    finally:
        cursor.close()
        conn.close()



def get_revenue_analytics() -> dict:
    """Get revenue analytics data."""

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        analytics = {}

        paid_status = 2   # Paid status id


        # Total Revenue
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0) AS total_revenue
            FROM payments
            WHERE payment_status_id = {paid_status}
        """)
        analytics["total_revenue"] = cursor.fetchone()["total_revenue"] or 0.0


        # Today's Revenue
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0) AS today_revenue
            FROM payments
            WHERE DATE(paid_at) = CURDATE()
            AND payment_status_id = {paid_status}
        """)
        analytics["today_revenue"] = cursor.fetchone()["today_revenue"] or 0.0


        # Weekly Revenue
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0) AS weekly_revenue
            FROM payments
            WHERE YEARWEEK(paid_at) = YEARWEEK(CURDATE())
            AND payment_status_id = {paid_status}
        """)
        analytics["weekly_revenue"] = cursor.fetchone()["weekly_revenue"] or 0.0


        # Monthly Revenue
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0) AS monthly_revenue
            FROM payments
            WHERE MONTH(paid_at)=MONTH(CURDATE())
            AND YEAR(paid_at)=YEAR(CURDATE())
            AND payment_status_id = {paid_status}
        """)
        analytics["monthly_revenue"] = cursor.fetchone()["monthly_revenue"] or 0.0


        # Yearly Revenue
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount),0) AS yearly_revenue
            FROM payments
            WHERE YEAR(paid_at)=YEAR(CURDATE())
            AND payment_status_id = {paid_status}
        """)
        analytics["yearly_revenue"] = cursor.fetchone()["yearly_revenue"] or 0.0


        # Average Ticket Price
        cursor.execute(f"""
            SELECT COALESCE(AVG(amount),0) AS avg_ticket_price
            FROM payments
            WHERE payment_status_id = {paid_status}
        """)
        analytics["avg_ticket_price"] = cursor.fetchone()["avg_ticket_price"] or 0.0


        # Daily Revenue Trend (Last 30 Days)
        cursor.execute(f"""
            SELECT
                DATE(paid_at) AS date,
                SUM(amount) AS revenue,
                COUNT(id) AS transaction_count
            FROM payments
            WHERE paid_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND payment_status_id = {paid_status}
            GROUP BY DATE(paid_at)
            ORDER BY date ASC
        """)

        daily = cursor.fetchall()

        analytics["daily_revenue"] = daily
        analytics["revenue_trend"] = daily


        # Revenue By Airline
        cursor.execute(f"""
            SELECT
                a.airline_name,
                a.airline_code,
                COUNT(b.id) AS total_bookings,
                SUM(p.amount) AS total_revenue,
                AVG(p.amount) AS avg_ticket_price

            FROM payments p

            JOIN bookings b
                ON p.booking_id = b.id

            JOIN flights f
                ON b.flight_id = f.id

            JOIN airlines a
                ON f.airline_id = a.id

            WHERE p.payment_status_id = {paid_status}

            GROUP BY
                a.id,
                a.airline_name,
                a.airline_code

            ORDER BY total_revenue DESC
        """)

        analytics["revenue_by_airline"] = cursor.fetchall()



        # Revenue By Route
        cursor.execute(f"""
            SELECT
                CONCAT(
                    ap1.airport_code,
                    ' → ',
                    ap2.airport_code
                ) AS route,

                ap1.city AS origin_city,
                ap2.city AS destination_city,

                COUNT(b.id) AS total_bookings,
                SUM(p.amount) AS total_revenue

            FROM payments p

            JOIN bookings b
                ON p.booking_id = b.id

            JOIN flights f
                ON b.flight_id = f.id

            JOIN airports ap1
                ON f.origin_airport_id = ap1.id

            JOIN airports ap2
                ON f.destination_airport_id = ap2.id

            WHERE p.payment_status_id = {paid_status}

            GROUP BY
                ap1.airport_code,
                ap2.airport_code,
                ap1.city,
                ap2.city

            ORDER BY total_revenue DESC

            LIMIT 20
        """)

        analytics["revenue_by_route"] = cursor.fetchall()


        print("REVENUE ANALYTICS:", analytics)

        return analytics


    finally:
        cursor.close()
        conn.close()
def get_booking_analytics() -> dict:
    """Get booking analytics data."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        analytics = {}
        
        # Booking status distribution
        cursor.execute("""
            SELECT bs.status_name, COUNT(b.id) AS count
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            GROUP BY bs.status_name
        """)
        status_data = {row["status_name"]: row["count"] for row in cursor.fetchall()}
        analytics["confirmed"] = status_data.get("Confirmed", 0)
        analytics["cancelled"] = status_data.get("Cancelled", 0)
        analytics["completed"] = status_data.get("Completed", 0)
        analytics["pending"] = status_data.get("Pending", 0)
        
        # Monthly booking trend
        cursor.execute("""
            SELECT 
                DATE_FORMAT(b.booked_at, ''%Y-%m'') AS month,
                COUNT(b.id) AS booking_count
            FROM bookings b
            WHERE b.booked_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(b.booked_at, ''%Y-%m'')
            ORDER BY month ASC
        """)
        analytics["monthly_trend"] = cursor.fetchall()
        
        return analytics
    
    finally:
        cursor.close()
        conn.close()


def get_user_analytics() -> dict:
    """Get user analytics data."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        analytics = {}
        
        # Total Registered Users
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        analytics["total_users"] = cursor.fetchone()["total"]
        
        # New Users (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) AS new_users
            FROM users
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        analytics["new_users"] = cursor.fetchone()["new_users"]
        
        # Frequent Travellers (more than 5 bookings)
        cursor.execute("""
            SELECT COUNT(*) AS frequent_travellers
            FROM users u
            WHERE (
                SELECT COUNT(*) FROM bookings b 
                WHERE b.user_id = u.id 
                AND b.booking_status_id != (SELECT id FROM booking_status WHERE status_name = 'Cancelled' LIMIT 1)
            ) > 5
        """)
        analytics["frequent_travellers"] = cursor.fetchone()["frequent_travellers"]
        
        # Inactive Users (no bookings)
        cursor.execute("""
            SELECT COUNT(*) AS inactive_users
            FROM users u
            WHERE NOT EXISTS (SELECT 1 FROM bookings b WHERE b.user_id = u.id)
        """)
        analytics["inactive_users"] = cursor.fetchone()["inactive_users"]
        
        # Top Customers by Spending
        cursor.execute("""
            SELECT 
                u.id, u.full_name, u.email,
                COUNT(DISTINCT b.id) AS total_bookings,
                COALESCE(SUM(p.amount), 0) AS total_spent
            FROM users u
            LEFT JOIN bookings b ON b.user_id = u.id
            LEFT JOIN payments p ON p.booking_id = b.id
                AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            GROUP BY u.id, u.full_name, u.email
            ORDER BY total_spent DESC
            LIMIT 10
        """)
        analytics["top_customers"] = cursor.fetchall()
        
        return analytics
    
    finally:
        cursor.close()
        conn.close()


def get_flight_analytics() -> dict:
    """Get flight analytics data."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        analytics = {}
        
        # Most Booked Flights
        cursor.execute("""
            SELECT 
                f.flight_number,
                a.airline_name,
                o.airport_code AS origin,
                d.airport_code AS destination,
                COUNT(b.id) AS total_bookings
            FROM flights f
            JOIN airlines a ON f.airline_id = a.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            LEFT JOIN bookings b ON b.flight_id = f.id
            LEFT JOIN booking_status bs ON b.booking_status_id = bs.id
                AND bs.status_name != 'Cancelled'
            GROUP BY f.id, f.flight_number, a.airline_name, o.airport_code, d.airport_code
            ORDER BY total_bookings DESC
            LIMIT 10
        """)
        analytics["most_booked_flights"] = cursor.fetchall()
        
        # Least Booked Flights
        cursor.execute("""
            SELECT 
                f.flight_number,
                a.airline_name,
                o.airport_code AS origin,
                d.airport_code AS destination,
                COUNT(b.id) AS total_bookings
            FROM flights f
            JOIN airlines a ON f.airline_id = a.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            LEFT JOIN bookings b ON b.flight_id = f.id
            LEFT JOIN booking_status bs ON b.booking_status_id = bs.id
                AND bs.status_name != 'Cancelled'
            GROUP BY f.id, f.flight_number, a.airline_name, o.airport_code, d.airport_code
            ORDER BY total_bookings ASC
            LIMIT 10
        """)
        analytics["least_booked_flights"] = cursor.fetchall()
        
        # Flight Occupancy Stats
        cursor.execute("""
            SELECT 
                f.flight_number,
                f.seats_economy,
                f.seats_business,
                COUNT(bp.id) AS booked_seats,
                ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_percentage
            FROM flights f
            LEFT JOIN bookings b ON b.flight_id = f.id
            LEFT JOIN booking_passengers bp ON bp.booking_id = b.id
            LEFT JOIN booking_status bs ON b.booking_status_id = bs.id
                AND bs.status_name != 'Cancelled'
            GROUP BY f.id, f.flight_number, f.seats_economy, f.seats_business
            ORDER BY occupancy_percentage DESC
        """)
        analytics["occupancy_stats"] = cursor.fetchall()
        
        return analytics
    
    finally:
        cursor.close()
        conn.close()


def get_route_analytics() -> dict:
    """Get route analytics data."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        analytics = {}
        
        # Top Routes
        cursor.execute("""
            SELECT 
                CONCAT(o.airport_code, ' → ', d.airport_code) AS route_name,
                o.city AS origin_city,
                d.city AS destination_city,
                COUNT(f.id) AS total_flights,
                COUNT(DISTINCT b.id) AS total_bookings,
                COALESCE(SUM(p.amount), 0) AS total_revenue
            FROM flights f
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            LEFT JOIN bookings b ON b.flight_id = f.id
            LEFT JOIN booking_status bs ON b.booking_status_id = bs.id
                AND bs.status_name != 'Cancelled'
            LEFT JOIN payments p ON p.booking_id = b.id
                AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            GROUP BY o.airport_code, d.airport_code, o.city, d.city
            ORDER BY total_bookings DESC
            LIMIT 10
        """)
        analytics["top_routes"] = cursor.fetchall()
        
        # Least Popular Routes
        cursor.execute("""
            SELECT 
                CONCAT(o.airport_code, ' → ', d.airport_code) AS route_name,
                o.city AS origin_city,
                d.city AS destination_city,
                COUNT(f.id) AS total_flights,
                COUNT(DISTINCT b.id) AS total_bookings
            FROM flights f
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            LEFT JOIN bookings b ON b.flight_id = f.id
            LEFT JOIN booking_status bs ON b.booking_status_id = bs.id
                AND bs.status_name != 'Cancelled'
            GROUP BY o.airport_code, d.airport_code, o.city, d.city
            ORDER BY total_bookings ASC
            LIMIT 10
        """)
        analytics["least_popular_routes"] = cursor.fetchall()
        
        # Highest Revenue Routes
        cursor.execute("""
            SELECT 
                CONCAT(o.airport_code, ' → ', d.airport_code) AS route_name,
                o.city AS origin_city,
                d.city AS destination_city,
                COALESCE(SUM(p.amount), 0) AS total_revenue
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN flights f ON b.flight_id = f.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            WHERE p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
            GROUP BY o.airport_code, d.airport_code, o.city, d.city
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        analytics["highest_revenue_routes"] = cursor.fetchall()
        
        return analytics
    
    finally:
        cursor.close()
        conn.close()