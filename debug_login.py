from models.user import get_db_connection, get_user_by_email, verify_password, hash_password

# Check admin user
user = get_user_by_email('admin@airline.com')
print(f"Admin user found: {user is not None}")
if user:
    print(f"User ID: {user['id']}")
    print(f"Full name: {user['full_name']}")
    print(f"Role: {user['role_name']}")
    
    # Test password verification with old and new passwords
    test_password = 'admin123'
    print(f"\nVerifying password '{test_password}': {verify_password(user['password_hash'], test_password)}")
    
    # Check if the new hash works
    new_hash = hash_password('admin123')
    print(f"Generated new hash: {new_hash[:50]}...")
    print(f"New hash verified: {verify_password(new_hash, 'admin123')}")
    
    # Try the database seed password
    print("\nChecking all users:")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, role_id FROM users")
    users = cursor.fetchall()
    for u in users:
        print(f"  User {u['id']}: {u['email']} (role_id: {u['role_id']})")
    cursor.close()
    conn.close()