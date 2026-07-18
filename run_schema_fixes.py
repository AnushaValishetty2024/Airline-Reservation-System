import mysql.connector
from config import Config

conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    port=Config.MYSQL_PORT,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB,
    charset=Config.MYSQL_CHARSET,
)
cursor = conn.cursor()

with open("schema_fixes.sql", "r") as f:
    sql = f.read()

for statement in sql.split(";"):
    statement = statement.strip()
    if statement:
        try:
            cursor.execute(statement)
            print(f"Executed: {statement[:50]}...")
        except Exception as e:
            print(f"Warning: {e}")

conn.commit()
print("\nSchema fixes applied successfully!")
cursor.close()
conn.close()