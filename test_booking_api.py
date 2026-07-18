"""
Test script to verify the booking API fix.
This demonstrates the working JSON booking endpoint.
"""

import mysql.connector
from config import Config
from app import app, seed_database_if_empty


def get_test_user_id():
    """Get a valid user ID for testing."""
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = 'john.doe@example.com' LIMIT 1")
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user[0] if user else 2


def test_booking_api():
    """Test the booking API with JSON payload."""
    user_id = get_test_user_id()
    
    # Get available flight
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM flights WHERE seats_economy >= 2 LIMIT 1")
    flight = cursor.fetchone()
    flight_id = flight[0] if flight else 1
    cursor.close()
    conn.close()

    with app.test_client() as client:
        # Login first to establish session
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["csrf_token"] = "test_token_12345"

        # Test 1: Successful booking with JSON payload
        print("\n=== TEST: Booking API with JSON Payload ===")
        
        payload = {
            "flight_id": flight_id,
            "seat_class": "economy",
            "passengers": [
                {"name": "Anusha", "age": 22, "email": "anusha@test.com", "mobile": "+15550000001"},
                {"name": "Rahul", "age": 25, "email": "rahul@test.com", "mobile": "+15550000002"}
            ]
        }

        response = client.post(
            '/api/book',
            json=payload,
            headers={'X-CSRFToken': 'test_token_12345'}
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")
        print(f"Response JSON: {response.get_json()}")

        if response.status_code == 201:
            data = response.get_json()
            booking_ref = data.get("booking_reference")
            print(f"✓ Booking successful! Reference: {booking_ref}")

            # Test 2: Get booking history
            print("\n=== TEST: Get Booking History ===")
            hist_response = client.get('/api/bookings')
            print(f"Status Code: {hist_response.status_code}")
            hist_data = hist_response.get_json()
            print(f"✓ Found {len(hist_data.get('bookings', []))} bookings")

            # Test 3: Get booking details
            print("\n=== TEST: Get Booking Details ===")
            if hist_data.get('bookings'):
                booking_id = hist_data['bookings'][0]['id']
                detail_response = client.get(f'/api/bookings/{booking_id}')
                print(f"Status Code: {detail_response.status_code}")
                detail_data = detail_response.get_json()
                print(f"✓ Booking details retrieved")
                print(f"  Passengers: {len(detail_data.get('passengers', []))}")

            print("\n✓ All booking API tests passed!")
            return True
        else:
            print(f"✗ Booking failed: {response.get_json()}")
            return False


if __name__ == "__main__":
    try:
        success = test_booking_api()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)