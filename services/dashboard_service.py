"""Dashboard service for user and admin dashboards."""
from mysql.connector import Error
from models.user import get_db_connection
from datetime import datetime, timedelta


def get_user_dashboard_kpis(user_id: int) -> dict:
    """Get KPI metrics for user dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        kpis = {}
        
        # Total Bookings
        cursor.execute("""
            SELECT COUNT(DISTINCT b.id) AS total_bookings
            FROM bookings b
            WHERE b.user_id = %s
        """, (user_id,))
        kpis["total_bookings"] = cursor.fetchone()["total_bookings"] or 0
        
        # Upcoming Trips (future departures with Confirmed or Pending status)
        cursor.execute("""
            SELECT COUNT(DISTINCT b.id) AS upcoming_trips
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
            AND f.departure_datetime > NOW()
            AND bs.status_name IN ('Confirmed', 'Pending')
        """, (user_id,))
        kpis["upcoming_trips"] = cursor.fetchone()["upcoming_trips"] or 0
        
        # Completed Trips (past arrivals with Completed status)
        cursor.execute("""
            SELECT COUNT(DISTINCT b.id) AS completed_trips
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
            AND f.arrival_datetime < NOW()
            AND bs.status_name IN ('Completed', 'Confirmed')
        """, (user_id,))
        kpis["completed_trips"] = cursor.fetchone()["completed_trips"] or 0
        
        # Cancelled Trips
        cursor.execute("""
            SELECT COUNT(DISTINCT b.id) AS cancelled_trips
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
            AND bs.status_name = 'Cancelled'
        """, (user_id,))
        kpis["cancelled_trips"] = cursor.fetchone()["cancelled_trips"] or 0
        
               # Favourite Airline
        cursor.execute("""
            SELECT a.airline_name, COUNT(b.id) AS booking_count
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            WHERE b.user_id = %s
            GROUP BY a.airline_name
            ORDER BY booking_count DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        kpis["favourite_airline"] = result["airline_name"] if result else "N/A"

        # Favourite Destination
        cursor.execute("""
            SELECT d.city AS destination, COUNT(b.id) AS booking_count
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airports d ON f.destination_airport_id = d.id
            WHERE b.user_id = %s
            GROUP BY d.city
            ORDER BY booking_count DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        kpis["favourite_destination"] = result["destination"] if result else "N/A"

        # Total Amount Spent
        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) AS total_spent
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN payment_status ps ON p.payment_status_id = ps.id
            WHERE b.user_id = %s AND ps.status_name = 'Paid'
        """, (user_id,))
        kpis["total_spent"] = cursor.fetchone()["total_spent"] or 0.0

        # Average Ticket Price
        cursor.execute("""
            SELECT COALESCE(AVG(p.amount), 0) AS avg_price
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN payment_status ps ON p.payment_status_id = ps.id
            WHERE b.user_id = %s AND ps.status_name = 'Paid'
        """, (user_id,))
        kpis["avg_ticket_price"] = cursor.fetchone()["avg_price"] or 0.0

        return kpis

    finally:
        cursor.close()
        conn.close()


def get_upcoming_trips(user_id):
    """Get upcoming trips for a user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                b.id AS booking_id,
                b.booking_reference,
                f.flight_number,
                a.airline_name,
                oa.airport_code AS origin_code,
                da.airport_code AS destination_code,
                f.departure_datetime,
                f.arrival_datetime,
                bs.status_name AS booking_status
            FROM bookings b
            JOIN flights f
                ON b.flight_id = f.id
            JOIN airlines a
                ON f.airline_id = a.id
            JOIN airports oa
                ON f.origin_airport_id = oa.id
            JOIN airports da
                ON f.destination_airport_id = da.id
            JOIN booking_status bs
                ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
              AND f.departure_datetime >= NOW()
            ORDER BY f.departure_datetime ASC
        """, (user_id,))

        return cursor.fetchall()

    except Error as e:
        print(f"Database Error: {e}")
        return []

    finally:
        cursor.close()
        conn.close()

def get_booking_history(user_id: int, search: str = "", status_filter: str = "", 
                        date_from: str = "", date_to: str = "", 
                        sort_by: str = "booked_at", sort_order: str = "DESC",
                        page: int = 1, per_page: int = 10) -> tuple:
    """
    Get paginated booking history with filters.
    Returns (bookings, total_count, total_pages)
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Build dynamic query
        where_clauses = ["b.user_id = %s"]
        params = [user_id]
        
        if search:
            where_clauses.append("(b.booking_reference LIKE %s OR f.flight_number LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if status_filter:
            where_clauses.append("bs.status_name = %s")
            params.append(status_filter)
        
        if date_from:
            where_clauses.append("DATE(b.booked_at) >= %s")
            params.append(date_from)
        
        if date_to:
            where_clauses.append("DATE(b.booked_at) <= %s")
            params.append(date_to)
        
        where_sql = " AND ".join(where_clauses)
        
        # Validate sort column
        allowed_sort = ["booked_at", "total_amount", "flight_number", "booking_status"]
        if sort_by not in allowed_sort:
            sort_by = "booked_at"
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "DESC"
        
        # Count total
        count_query = f"""
            SELECT COUNT(DISTINCT b.id) AS total
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            JOIN flights f ON b.flight_id = f.id
            WHERE {where_sql}
        """
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get paginated results
        query = f"""
            SELECT 
                b.id, b.booking_reference, b.total_amount, b.booked_at,
                bs.status_name AS booking_status,
                f.flight_number,
                o.airport_code AS origin_code,
                d.airport_code AS destination_code,
                o.city AS origin_city,
                d.city AS destination_city,
                f.departure_datetime,
                f.arrival_datetime,
                a.airline_name,
                bs.id AS status_id,
                p.payment_method,
                ps.status_name AS payment_status
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            LEFT JOIN payments p ON p.booking_id = b.id
            LEFT JOIN payment_status ps ON p.payment_status_id = ps.id
            WHERE {where_sql}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [per_page, offset])
        bookings = cursor.fetchall()
        
        total_pages = (total + per_page - 1) // per_page
        
        return bookings, total, total_pages
    
    finally:
        cursor.close()
        conn.close()


def get_booking_details_enriched(booking_id: int, user_id: int) -> dict:
    """Get enriched booking details for ticket/invoice generation."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get booking with all related info
        cursor.execute("""
            SELECT 
                b.id, b.booking_reference, b.total_amount, b.booked_at,
                bs.status_name AS booking_status,
                f.flight_number, f.departure_datetime, f.arrival_datetime,
                f.economy_price, f.business_price,
                a.airline_name,
                o.airport_code AS origin_code, o.city AS origin_city,
                d.airport_code AS destination_code, d.city AS destination_city,
                ac.aircraft_model,
                p.payment_reference, p.amount AS amount_paid, p.payment_method,
                ps.status_name AS payment_status,
                t.ticket_number,
                inv.invoice_number
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            JOIN aircraft ac ON f.aircraft_id = ac.id
            LEFT JOIN payments p ON p.booking_id = b.id
            LEFT JOIN payment_status ps ON p.payment_status_id = ps.id
            LEFT JOIN tickets t ON t.booking_id = b.id
            LEFT JOIN invoices inv ON inv.booking_id = b.id
            WHERE b.id = %s AND b.user_id = %s
        """, (booking_id, user_id))
        
        booking = cursor.fetchone()
        if not booking:
            return None
        
        # Get passengers
        cursor.execute("""
            SELECT p.full_name, p.email, p.mobile_number, p.passport_number,
                   p.gender, p.date_of_birth, bp.seat_number, ts.status_name AS ticket_status
            FROM booking_passengers bp
            JOIN passengers p ON bp.passenger_id = p.id
            JOIN ticket_status ts ON bp.ticket_status_id = ts.id
            WHERE bp.booking_id = %s
        """, (booking_id,))
        passengers = cursor.fetchall()
        
        booking["passengers"] = passengers
        return booking
    
    finally:
        cursor.close()
        conn.close()


def get_upcoming_trips(user_id: int) -> list:
    """Get upcoming trips for user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                b.id,
                b.booking_reference,
                b.total_amount,
                bs.status_name AS booking_status,

                f.flight_number,
                a.airline_name,

                o.airport_code AS origin_code,
                o.city AS origin_city,

                d.airport_code AS destination_code,
                d.city AS destination_city,

                f.departure_datetime,
                f.arrival_datetime,

                bp.seat_number,

                COUNT(bp.id) AS passenger_count

            FROM bookings b

            JOIN booking_status bs
                ON b.booking_status_id = bs.id

            JOIN flights f
                ON b.flight_id = f.id

            JOIN airlines a
                ON f.airline_id = a.id

            JOIN airports o
                ON f.origin_airport_id = o.id

            JOIN airports d
                ON f.destination_airport_id = d.id

            LEFT JOIN booking_passengers bp
                ON bp.booking_id = b.id

            WHERE b.user_id = %s
              AND f.departure_datetime > NOW()
              AND bs.status_name IN ('Confirmed','Pending')

            GROUP BY
                b.id,
                b.booking_reference,
                b.total_amount,
                bs.status_name,
                f.flight_number,
                a.airline_name,
                o.airport_code,
                o.city,
                d.airport_code,
                d.city,
                f.departure_datetime,
                f.arrival_datetime,
                bp.seat_number

            ORDER BY f.departure_datetime ASC
        """, (user_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def get_user_analytics(user_id: int) -> dict:
    """Get travel analytics for user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        analytics = {}
        
        # Total Flights
        cursor.execute("""
            SELECT COUNT(DISTINCT f.id) AS total_flights
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            WHERE b.user_id = %s
        """, (user_id,))
        analytics["total_flights"] = cursor.fetchone()["total_flights"] or 0
        
        # Favourite Airline
        cursor.execute("""
            SELECT a.airline_name
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            WHERE b.user_id = %s
            GROUP BY a.airline_name
            ORDER BY COUNT(b.id) DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        analytics["favourite_airline"] = result["airline_name"] if result else "N/A"
        
        # Favourite Destination
        cursor.execute("""
            SELECT d.city
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airports d ON f.destination_airport_id = d.id
            WHERE b.user_id = %s
            GROUP BY d.city
            ORDER BY COUNT(b.id) DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        analytics["favourite_destination"] = result["city"] if result else "N/A"
        
        # Total Money Spent
        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) AS total_spent
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN payment_status ps ON p.payment_status_id = ps.id
            WHERE b.user_id = %s AND ps.status_name = 'Paid'
        """, (user_id,))
        analytics["total_spent"] = cursor.fetchone()["total_spent"] or 0.0
        
        # Average Ticket Price
        cursor.execute("""
            SELECT COALESCE(AVG(p.amount), 0) AS avg_price
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN payment_status ps ON p.payment_status_id = ps.id
            WHERE b.user_id = %s AND ps.status_name = 'Paid'
        """, (user_id,))
        analytics["avg_ticket_price"] = cursor.fetchone()["avg_price"] or 0.0
        
        # Last Trip - exclude cancelled bookings.
        # Prefer completed journey; otherwise latest confirmed flight whose arrival has passed.
        cursor.execute("""
            SELECT f.flight_number, o.airport_code AS origin,
                   d.airport_code AS destination, f.departure_datetime,
                   f.arrival_datetime, bs.status_name AS status
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
              AND bs.status_name IN ('Completed', 'Confirmed')
            ORDER BY
                CASE WHEN bs.status_name = 'Completed' THEN 1 ELSE 2 END,
                f.departure_datetime DESC
            LIMIT 1
        """, (user_id,))
        analytics["last_trip"] = cursor.fetchone()
        
        # Next Trip
        cursor.execute("""
            SELECT f.flight_number, o.airport_code AS origin,
                   d.airport_code AS destination, f.departure_datetime,
                   bs.status_name AS status
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
            AND f.departure_datetime > NOW()
            AND bs.status_name IN ('Confirmed', 'Pending')
            ORDER BY f.departure_datetime ASC
            LIMIT 1
        """, (user_id,))
        analytics["next_trip"] = cursor.fetchone()
        
        # Most Used Route
        cursor.execute("""
            SELECT
                CONCAT(o.airport_code, ' → ', d.airport_code) AS route_name,
                o.city AS origin_city,
                d.city AS destination_city,
                COUNT(b.id) AS usage_count
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airports o ON f.origin_airport_id = o.id
            JOIN airports d ON f.destination_airport_id = d.id
            WHERE b.user_id = %s
            GROUP BY o.airport_code, d.airport_code, o.city, d.city
            ORDER BY usage_count DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        analytics["most_used_route"] = result["route_name"] if result else "N/A"

        # Monthly Spending (last 12 months including zero months)

        print("Running monthly spending query...")
        print(f"User ID: {user_id}")

        cursor.execute("""
           SELECT DATE_FORMAT(p.paid_at, '%Y-%m') AS month_key,
               COALESCE(SUM(p.amount), 0) AS total_spent
           FROM payments p
           JOIN bookings b ON p.booking_id = b.id
           JOIN payment_status ps ON p.payment_status_id = ps.id
           WHERE b.user_id = %s
               AND ps.status_name = 'Paid'
               AND p.paid_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
           GROUP BY DATE_FORMAT(p.paid_at, '%Y-%m')
           ORDER BY month_key ASC
        """, (user_id,))

        monthly_results = cursor.fetchall()

        print("Monthly Results:")
        print(monthly_results)
        monthly_map = {row["month_key"]: float(row["total_spent"]) for row in monthly_results}

        monthly_labels = []
        monthly_spending = []
        current_date = datetime.now()
                # Monthly Booking Count (last 12 months) for Issue 5 extra analytics
        cursor.execute("""
            SELECT
                DATE_FORMAT(b.booked_at, '%Y-%m') AS month_key,
                COUNT(b.id) AS booking_count
            FROM bookings b
            WHERE b.user_id = %s
              AND b.booked_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(b.booked_at, '%Y-%m')
            ORDER BY month_key ASC
        """, (user_id,))

        monthly_booking_results = cursor.fetchall()
        monthly_booking_map = {
            row["month_key"]: int(row["booking_count"])
            for row in monthly_booking_results
        }

        monthly_booking_labels = list(monthly_labels)
        monthly_booking_count = []
        current_date2 = datetime.now()

        for i in range(11, -1, -1):
            month_date = current_date2 - timedelta(days=30 * i)
            month_key = month_date.strftime('%Y-%m')
            monthly_booking_count.append(monthly_booking_map.get(month_key, 0))

        analytics["monthly_booking_labels"] = monthly_booking_labels
        analytics["monthly_booking_count"] = monthly_booking_count
        print("========== ANALYTICS ==========")
        print(analytics.keys())
        print(analytics)
        print("===============================")

        return analytics

        # Booking Status Distribution for Issue 5 extra analytics
        cursor.execute("""
            SELECT bs.status_name, COUNT(b.id) AS count
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
            GROUP BY bs.status_name
        """, (user_id,))
        status_distribution = {row["status_name"]: int(row["count"]) for row in cursor.fetchall()}
        analytics["booking_status_distribution"] = {
            "Confirmed": status_distribution.get("Confirmed", 0),
            "Pending": status_distribution.get("Pending", 0),
            "Cancelled": status_distribution.get("Cancelled", 0),
            "Completed": status_distribution.get("Completed", 0),
        }

        # Payment Method Distribution for Issue 5 extra analytics
        cursor.execute("""
            SELECT p.payment_method, COUNT(b.id) AS count
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            WHERE b.user_id = %s
            GROUP BY p.payment_method
        """, (user_id,))
        analytics["payment_method_distribution"] = {row["payment_method"]: int(row["count"]) for row in cursor.fetchall()}

        # Airline Distribution for Issue 5 extra analytics
        cursor.execute("""
            SELECT a.airline_name, COUNT(b.id) AS count
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN airlines a ON f.airline_id = a.id
            WHERE b.user_id = %s
            GROUP BY a.airline_name
            ORDER BY count DESC
        """, (user_id,))
        analytics["airline_distribution"] = {row["airline_name"]: int(row["count"]) for row in cursor.fetchall()}

        # Booking Trends by Status
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN bs.status_name = 'Confirmed' THEN 1 ELSE 0 END), 0) AS confirmed_bookings,
                COALESCE(SUM(CASE WHEN bs.status_name = 'Pending' THEN 1 ELSE 0 END), 0) AS pending_bookings,
                COALESCE(SUM(CASE WHEN bs.status_name = 'Cancelled' THEN 1 ELSE 0 END), 0) AS cancelled_bookings,
                COALESCE(SUM(CASE WHEN bs.status_name = 'Completed' THEN 1 ELSE 0 END), 0) AS completed_bookings
            FROM bookings b
            JOIN booking_status bs ON b.booking_status_id = bs.id
            WHERE b.user_id = %s
        """, (user_id,))
        status_counts = cursor.fetchone()
        analytics["confirmed_bookings"] = status_counts["confirmed_bookings"] if status_counts else 0
        analytics["pending_bookings"] = status_counts["pending_bookings"] if status_counts else 0
        analytics["cancelled_bookings"] = status_counts["cancelled_bookings"] if status_counts else 0
        analytics["completed_bookings"] = status_counts["completed_bookings"] if status_counts else 0

        return analytics
    
    finally:
        cursor.close()
        conn.close()