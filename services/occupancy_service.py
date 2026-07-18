from models.db import get_db_connection


class OccupancyService:

    def get_occupancy_data(self):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
SELECT
    f.id,
    f.flight_number,
    (f.seats_economy + f.seats_business) AS total_seats,

    COUNT(DISTINCT bp.id) AS booked_seats

FROM flights f

LEFT JOIN bookings b
    ON f.id = b.flight_id

LEFT JOIN booking_passengers bp
    ON b.id = bp.booking_id

GROUP BY 
    f.id,
    f.flight_number,
    f.seats_economy,
    f.seats_business

"""

        cursor.execute(query)

        flights = cursor.fetchall()

        occupancy_data = []

        for flight in flights:

            total = flight["total_seats"]
            booked = flight["booked_seats"]

            occupancy = 0

            if total > 0:
                occupancy = round(
                    (booked / total) * 100,
                    2
             )

            if occupancy > 100:
                occupancy = 100

            if booked > 0:

             occupancy_data.append({

        "flight": flight["flight_number"],
        "capacity": total,
        "booked": booked,
        "occupancy": occupancy

    })
        conn.close()

        return occupancy_data