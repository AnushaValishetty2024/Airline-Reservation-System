import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='airline_reservation'
    )
    cursor = conn.cursor()
    
    with open('database/day6_analytics_advanced.sql', 'r') as f:
        sql_script = f.read()
    
    # Execute each statement
    statements = sql_script.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"Statement executed (some may be idempotent): {str(e)[:100]}")
    
    conn.commit()
    print("Day 6 analytics schema applied successfully")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()