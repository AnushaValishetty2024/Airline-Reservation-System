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

with open('database/seed_indian_flights.sql', 'r') as f:
    sql = f.read()
    
for statement in sql.split(';'):
    statement = statement.strip()
    if statement:
        try:
            cursor.execute(statement)
        except Exception as e:
            print(f'Error: {e}')
            
conn.commit()
print('Database seeded successfully')
cursor.close()
conn.close()