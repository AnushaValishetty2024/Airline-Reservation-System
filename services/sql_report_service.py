from models.db import get_db_connection

def get_revenue_report():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vw_revenue_summary
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data



def get_booking_report():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vw_booking_summary
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data



def get_customer_report():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vw_customer_summary
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data



def get_flight_report():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vw_flight_performance
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data



def get_route_report():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM vw_route_performance
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data