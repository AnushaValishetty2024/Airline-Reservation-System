from models.user import get_db_connection, hash_password

# Reset admin password to a known value
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute(
    "UPDATE users SET password_hash = %s WHERE email = 'admin@airline.com'",
    (hash_password('admin123'),)
)
conn.commit()
cursor.close()
conn.close()
print("Admin password reset to: admin123")