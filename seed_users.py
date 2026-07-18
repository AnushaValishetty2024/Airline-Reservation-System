from models.user import get_db_connection, hash_password, get_user_by_email

# Seed users if not exist
conn = get_db_connection()
cursor = conn.cursor()

# Check if admin exists
admin = get_user_by_email('admin@airline.com')
if not admin:
    cursor.execute(
        "INSERT INTO users (full_name, email, mobile_number, password_hash, role_id) VALUES (%s, %s, %s, %s, %s)",
        ('System Administrator', 'admin@airline.com', '+15551234567', hash_password('admin123'), 1)
    )
    print("Admin user created with password: admin123")
else:
    print(f"Admin user already exists (ID: {admin['id']})")

# Check if test user exists
test_user = get_user_by_email('john.doe@example.com')
if not test_user:
    cursor.execute(
        "INSERT INTO users (full_name, email, mobile_number, password_hash, role_id) VALUES (%s, %s, %s, %s, %s)",
        ('John Doe', 'john.doe@example.com', '+15557654321', hash_password('password123'), 2)
    )
    print("Test user created with password: password123")
else:
    print(f"Test user already exists (ID: {test_user['id']})")

conn.commit()
cursor.close()
conn.close()

print("\nUsers seeded successfully!")