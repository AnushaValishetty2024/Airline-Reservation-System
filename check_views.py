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
cursor.execute('SHOW FULL TABLES WHERE Table_type = "VIEW"')
views = [t[0] for t in cursor.fetchall()]
print(f"Views count: {len(views)}")
for v in views:
    print(v)
cursor.close()
conn.close()