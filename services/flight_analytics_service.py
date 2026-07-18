from models.user import get_db_connection


# ===============================
# Best Performing Routes
# ===============================

def get_best_routes(limit=10):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
SELECT

    CONCAT(
        a1.airport_code,
        ' - ',
        a2.airport_code
    ) AS route,

    COUNT(b.id) AS total_bookings,

    SUM(p.amount) AS revenue

FROM bookings b

JOIN flights f
    ON b.flight_id = f.id

JOIN airports a1
    ON f.origin_airport_id = a1.id

JOIN airports a2
    ON f.destination_airport_id = a2.id

LEFT JOIN payments p
    ON b.id = p.booking_id

GROUP BY route

ORDER BY revenue DESC

LIMIT %s
"""

    cursor.execute(query, (limit,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data



# ===============================
# Highest Revenue Flights
# ===============================

def get_highest_revenue_flights(limit=10):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    query = """

    SELECT

        f.flight_number,

        al.airline_name AS airline,

        SUM(p.amount) AS revenue,

        COUNT(b.id) AS bookings


    FROM flights f


    JOIN airlines al

        ON f.airline_id = al.id


    JOIN bookings b

        ON f.id = b.flight_id


    JOIN payments p

        ON b.id = p.booking_id


    GROUP BY f.id


    ORDER BY revenue DESC


    LIMIT %s

    """


    cursor.execute(query,(limit,))


    data = cursor.fetchall()


    cursor.close()
    conn.close()


    return data





# ===============================
# Most Booked Flights
# ===============================

def get_most_booked_flights(limit=10):

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)


    query = """

    SELECT

        f.flight_number,

        al.airline_name AS airline,

        COUNT(b.id) AS total_bookings


    FROM flights f


    JOIN airlines al

        ON f.airline_id = al.id


    JOIN bookings b

        ON f.id = b.flight_id


    GROUP BY f.id


    ORDER BY total_bookings DESC


    LIMIT %s

    """


    cursor.execute(query,(limit,))


    data = cursor.fetchall()


    cursor.close()

    conn.close()


    return data
