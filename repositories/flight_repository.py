from models.db import get_db_connection


def get_airlines():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, airline_name, airline_code FROM airlines WHERE is_active = 1 ORDER BY airline_name")
    airlines = cursor.fetchall()
    cursor.close()
    conn.close()
    return airlines


def get_airports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, airport_name, airport_code, city, country FROM airports WHERE is_active = 1 ORDER BY city")
    airports = cursor.fetchall()
    cursor.close()
    conn.close()
    return airports


def get_aircraft():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, aircraft_model, seating_capacity FROM aircraft WHERE is_active = 1 ORDER BY aircraft_model")
    aircraft = cursor.fetchall()
    cursor.close()
    conn.close()
    return aircraft


def get_all_flights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT f.id, f.flight_number, a.airline_name, ac.aircraft_model, o.airport_code AS origin_code, o.city AS origin_city, "
        "d.airport_code AS destination_code, d.city AS destination_city, f.departure_datetime, f.arrival_datetime, "
        "f.economy_price, f.business_price, f.status, f.is_active "
        "FROM flights f "
        "INNER JOIN airlines a ON f.airline_id = a.id "
        "INNER JOIN aircraft ac ON f.aircraft_id = ac.id "
        "INNER JOIN airports o ON f.origin_airport_id = o.id "
        "INNER JOIN airports d ON f.destination_airport_id = d.id "
        "ORDER BY f.departure_datetime"
    )
    flights = cursor.fetchall()
    cursor.close()
    conn.close()
    return flights


def create_flight(flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
                  departure_datetime, arrival_datetime, economy_price, business_price, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO flights (flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id, "
        "departure_datetime, arrival_datetime, economy_price, business_price, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
         departure_datetime, arrival_datetime, economy_price, business_price, status),
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_flight(flight_id, flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
                  departure_datetime, arrival_datetime, economy_price, business_price, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE flights SET flight_number=%s, airline_id=%s, aircraft_id=%s, origin_airport_id=%s, "
        "destination_airport_id=%s, departure_datetime=%s, arrival_datetime=%s, economy_price=%s, "
        "business_price=%s, status=%s WHERE id=%s",
        (flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id,
         departure_datetime, arrival_datetime, economy_price, business_price, status, flight_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_flight(flight_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flights WHERE id = %s", (flight_id,))
    conn.commit()
    cursor.close()
    conn.close()


def toggle_flight_status(flight_id: int):
    """Toggle flight active/inactive status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE flights SET is_active = NOT is_active WHERE id = %s", (flight_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.rowcount > 0


def get_flight_by_id(flight_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT f.id, f.flight_number, a.airline_name, ac.aircraft_model, o.airport_code AS origin_code, o.city AS origin_city, "
        "d.airport_code AS destination_code, d.city AS destination_city, f.departure_datetime, f.arrival_datetime, "
        "f.economy_price, f.business_price, f.status, f.seats_economy, f.seats_business "
        "FROM flights f "
        "INNER JOIN airlines a ON f.airline_id = a.id "
        "INNER JOIN aircraft ac ON f.aircraft_id = ac.id "
        "INNER JOIN airports o ON f.origin_airport_id = o.id "
        "INNER JOIN airports d ON f.destination_airport_id = d.id "
        "WHERE f.id = %s",
        (flight_id,),
    )
    flight = cursor.fetchone()
    cursor.close()
    conn.close()
    return flight


def search_flights(origin_id=None, destination_id=None, departure_date=None, sort_by="departure_datetime",
                   airline_id=None, min_price=None, max_price=None, time_of_day=None, passenger_count=1):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = (
        "SELECT f.id, f.flight_number, a.airline_name, ac.aircraft_model, o.airport_code AS origin_code, o.city AS origin_city, "
        "d.airport_code AS destination_code, d.city AS destination_city, f.departure_datetime, f.arrival_datetime, "
        "f.economy_price, f.business_price, f.status, "
        "TIMEDIFF(f.arrival_datetime, f.departure_datetime) as duration, "
        "f.seats_economy, f.seats_business "
        "FROM flights f "
        "INNER JOIN airlines a ON f.airline_id = a.id "
        "INNER JOIN aircraft ac ON f.aircraft_id = ac.id "
        "INNER JOIN airports o ON f.origin_airport_id = o.id "
        "INNER JOIN airports d ON f.destination_airport_id = d.id "
        "WHERE 1=1"
    )
    params = []

    if origin_id:
        query += " AND f.origin_airport_id = %s"
        params.append(origin_id)
    if destination_id:
        query += " AND f.destination_airport_id = %s"
        params.append(destination_id)
    if departure_date:
        query += " AND DATE(f.departure_datetime) = %s"
        params.append(departure_date)
    if airline_id:
        query += " AND f.airline_id = %s"
        params.append(airline_id)

    # Time of day filter
    if time_of_day:
        if time_of_day == "morning":
            query += " AND HOUR(f.departure_datetime) >= 6 AND HOUR(f.departure_datetime) < 12"
        elif time_of_day == "afternoon":
            query += " AND HOUR(f.departure_datetime) >= 12 AND HOUR(f.departure_datetime) < 18"
        elif time_of_day == "evening":
            query += " AND HOUR(f.departure_datetime) >= 18 AND HOUR(f.departure_datetime) < 21"
        elif time_of_day == "night":
            query += " AND (HOUR(f.departure_datetime) >= 21 OR HOUR(f.departure_datetime) < 6)"

    # Price filter
    if min_price is not None:
        query += " AND f.economy_price >= %s"
        params.append(min_price)
    if max_price is not None:
        query += " AND f.economy_price <= %s"
        params.append(max_price)

    # Sorting
    if sort_by == "price_asc":
        query += " ORDER BY f.economy_price ASC"
    elif sort_by == "price_desc":
        query += " ORDER BY f.economy_price DESC"
    elif sort_by == "departure_earliest":
        query += " ORDER BY f.departure_datetime ASC"
    elif sort_by == "departure_latest":
        query += " ORDER BY f.departure_datetime DESC"
    elif sort_by == "duration_shortest":
        query += " ORDER BY TIMEDIFF(f.arrival_datetime, f.departure_datetime) ASC"
    else:
        query += " ORDER BY f.departure_datetime ASC"

    cursor.execute(query, tuple(params))
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    return flights