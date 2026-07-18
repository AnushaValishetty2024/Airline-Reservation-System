from models.user import get_db_connection



def get_cancellation_metrics():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    # Total bookings
    cursor.execute("""
        SELECT COUNT(*) AS total_bookings
        FROM bookings
    """)

    total = cursor.fetchone()["total_bookings"]



    # Cancelled bookings
    cursor.execute("""
        SELECT COUNT(*) AS cancelled

        FROM bookings b

        JOIN booking_status bs
        ON b.booking_status_id = bs.id

        WHERE bs.status_name = 'Cancelled'
    """)


    cancelled = cursor.fetchone()["cancelled"]



    cancellation_rate = 0

    if total > 0:
        cancellation_rate = round(
            (cancelled / total) * 100,
            2
        )


    data = {
    "total_bookings": total,
    "cancelled_bookings": cancelled,
    "cancellation_rate": cancellation_rate
}

    cursor.close()
    conn.close()

    return data




def get_cancelled_routes():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("""
        SELECT

            f.origin_airport_id,
            f.destination_airport_id,

            COUNT(*) AS cancellations


        FROM bookings b


        JOIN booking_status bs
        ON b.booking_status_id = bs.id


        JOIN flights f
        ON b.flight_id = f.id


        WHERE bs.status_name = 'Cancelled'


        GROUP BY

            f.origin_airport_id,
            f.destination_airport_id


        ORDER BY cancellations DESC


        LIMIT 10

    """)


    return cursor.fetchall()





def get_monthly_cancellation_trend():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("""
        SELECT

            DATE_FORMAT(b.booked_at,'%Y-%m') AS month,

            COUNT(*) AS cancellations


        FROM bookings b


        JOIN booking_status bs
        ON b.booking_status_id = bs.id


        WHERE bs.status_name = 'Cancelled'


        GROUP BY month


        ORDER BY month

    """)


    return cursor.fetchall()