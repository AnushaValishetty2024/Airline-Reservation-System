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

cursor.execute("SELECT COUNT(*) FROM flights")
flight_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM airlines")
airline_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM airports")
airport_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM aircraft")
aircraft_count = cursor.fetchone()[0]

print(f"Airlines: {airline_count}")
print(f"Airports: {airport_count}")
print(f"Aircraft: {aircraft_count}")
print(f"Flights: {flight_count}")

cursor.close()
conn.close()