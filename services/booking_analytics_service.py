from models.db import get_db_connection


def get_booking_trend_analytics():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    analytics = {}

    try:

        # -----------------------------
        # Daily Booking Trend
        # -----------------------------
        cursor.execute("""
            SELECT 
                DATE(created_at) AS booking_date,
                COUNT(*) AS total_bookings
            FROM bookings
            GROUP BY DATE(created_at)
            ORDER BY booking_date
        """)

        daily = cursor.fetchall()

        analytics["daily_bookings"] = {
            "labels": [
                str(row["booking_date"])
                for row in daily
            ],
            "values": [
                row["total_bookings"]
                for row in daily
            ]
        }


        # -----------------------------
        # Monthly Booking Trend
        # -----------------------------
        cursor.execute("""
            SELECT
                DATE_FORMAT(created_at,'%Y-%m') AS month,
                COUNT(*) AS total_bookings
            FROM bookings
            GROUP BY DATE_FORMAT(created_at,'%Y-%m')
            ORDER BY month
        """)

        monthly = cursor.fetchall()


        analytics["monthly_bookings"] = {
            "labels": [
                row["month"]
                for row in monthly
            ],
            "values": [
                row["total_bookings"]
                for row in monthly
            ]
        }


        # -----------------------------
        # Peak Booking Hours
        # -----------------------------
        cursor.execute("""
            SELECT
                HOUR(created_at) AS booking_hour,
                COUNT(*) AS total_bookings
            FROM bookings
            GROUP BY HOUR(created_at)
            ORDER BY total_bookings DESC
            LIMIT 5
        """)


        hours = cursor.fetchall()


        analytics["peak_booking_hours"] = {
            "labels": [
                f"{row['booking_hour']}:00"
                for row in hours
            ],
            "values": [
                row["total_bookings"]
                for row in hours
            ]
        }



        # -----------------------------
        # Peak Booking Days
        # -----------------------------
        cursor.execute("""
            SELECT
                DAYNAME(created_at) AS booking_day,
                COUNT(*) AS total_bookings
            FROM bookings
            GROUP BY DAYNAME(created_at)
            ORDER BY total_bookings DESC
        """)


        days = cursor.fetchall()


        analytics["peak_booking_days"] = {
            "labels": [
                row["booking_day"]
                for row in days
            ],
            "values": [
                row["total_bookings"]
                for row in days
            ]
        }


        return analytics


    except Exception as e:
        print("Booking Analytics Error:", e)
        return {}


    finally:
        cursor.close()
        conn.close()