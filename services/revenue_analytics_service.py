from models.db import get_db_connection


def get_revenue_analytics():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    analytics = {}

    try:

        # Total Revenue
        cursor.execute("""
            SELECT 
            COALESCE(SUM(amount),0) AS total_revenue
            FROM payments
        """)

        analytics["total_revenue"] = cursor.fetchone()["total_revenue"]


        # Revenue By Airline
        cursor.execute("""
            SELECT
            a.airline_name,
            SUM(p.amount) AS revenue

            FROM payments p

            JOIN bookings b
            ON p.booking_id=b.id

            JOIN flights f
            ON b.flight_id=f.id

            JOIN airlines a
            ON f.airline_id=a.id

            GROUP BY a.airline_name

            ORDER BY revenue DESC
        """)

        analytics["airline_revenue"] = cursor.fetchall()



        # Monthly Revenue

        cursor.execute("""
            SELECT

            MONTH(paid_at) AS month,

            SUM(amount) AS revenue

            FROM payments

            GROUP BY MONTH(paid_at)

            ORDER BY month

        """)

        analytics["monthly_revenue"] = cursor.fetchall()



        # Revenue By Route

        cursor.execute("""
            SELECT

            CONCAT(
            f.origin_airport_id,
            ' - ',
            f.destination_airport_id
            )
            AS route,

            SUM(p.amount) AS revenue


            FROM payments p


            JOIN bookings b
            ON p.booking_id=b.id


            JOIN flights f
            ON b.flight_id=f.id


            GROUP BY route


            ORDER BY revenue DESC

            LIMIT 10

        """)


        analytics["route_revenue"] = cursor.fetchall()



        return analytics


    finally:

        cursor.close()
        conn.close()