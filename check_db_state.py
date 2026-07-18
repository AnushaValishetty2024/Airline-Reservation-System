import mysql.connector
from config import Config

conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    port=Config.MYSQL_PORT,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB
)
cursor = conn.cursor()

print("=== Flights ===")
cursor.execute("SELECT id, flight_number, seats_economy, seats_business FROM flights")
for row in cursor.fetchall():
    print(row)

print("\n=== Booking Count ===")
cursor.execute("SELECT COUNT(*) FROM bookings")
print("Total bookings:", cursor.fetchone()[0])

print("\n=== Booking Passengers Count ===")
cursor.execute("SELECT COUNT(*) FROM booking_passengers")
print("Total booking_passengers:", cursor.fetchone()[0])

print("\n=== Recent Bookings ===")
cursor.execute("""
    SELECT b.id, b.booking_reference, b.flight_id, b.booking_status_id, bs.status_name
    FROM bookings b
    JOIN booking_status bs ON b.booking_status_id = bs.id
    ORDER BY b.id DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()