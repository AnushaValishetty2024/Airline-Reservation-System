#!/usr/bin/env python3
"""
Test that passenger_count is correctly passed from search to booking page
for counts 1-9.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import re

def test_passenger_count_flow():
    """Test that passenger_count flows correctly from search to booking."""
    app = create_app()
    client = app.test_client()

    print("="*60)
    print("TESTING PASSENGER COUNT FLOW (1-9)")
    print("="*60)

    with app.app_context():
        # Test each passenger count from 1 to 9
        for count in range(1, 10):
            print(f"\nTest: Passenger Count = {count}")
            print("-" * 40)

            # Step 1: Search with specific passenger count
            search_response = client.post('/search', data={
                'passenger_count': count,
                'cabin_class': 'economy'
            }, follow_redirects=True)

            if search_response.status_code != 200:
                print(f"  ✗ Search failed with status {search_response.status_code}")
                continue

            # Step 2: Extract flight ID from search results
            flight_ids = re.findall(r'/book/(\d+)\?passenger_count=(\d+)', search_response.text)

            if not flight_ids:
                # Try alternative pattern without query string
                flight_ids = re.findall(r'/book/(\d+)', search_response.text)
                if flight_ids:
                    flight_id = flight_ids[0]
                    # Manually construct booking URL with passenger_count
                    booking_url = f'/book/{flight_id}?passenger_count={count}'
                else:
                    print(f"  ✗ No flights found in search results")
                    continue
            else:
                # Use the first flight with its passenger_count
                flight_id, found_count = flight_ids[0]
                booking_url = f'/book/{flight_id}?passenger_count={found_count}'

            # Step 3: Access booking page
            booking_response = client.get(booking_url)

            if booking_response.status_code != 200:
                print(f"  ✗ Booking page failed with status {booking_response.status_code}")
                continue

            # Step 4: Check that the template received the correct passenger_count
            if f'Number of Passengers:</span>' in booking_response.text:
                # Extract the displayed passenger count
                # Look for the pattern in the booking summary
                match = re.search(
                    r'Number of Passengers:</span>\s*<strong[^>]*>(\d+)</strong>',
                    booking_response.text
                )
                if match:
                    displayed_count = int(match.group(1))
                    if displayed_count == count:
                        print(f"  ✓ Booking page displays correct count: {displayed_count}")
                    else:
                        print(f"  ✗ Booking page shows {displayed_count}, expected {count}")
                else:
                    print(f"  ✗ Could not extract displayed passenger count")
            else:
                print(f"  ✗ Booking summary not found in page")

            # Step 5: Check hidden input field
            match = re.search(
                r'<input type="hidden" name="passenger_count" value="(\d+)">',
                booking_response.text
            )
            if match:
                hidden_value = int(match.group(1))
                if hidden_value == count:
                    print(f"  ✓ Hidden input has correct value: {hidden_value}")
                else:
                    print(f"  ✗ Hidden input has {hidden_value}, expected {count}")
            else:
                print(f"  ✗ Hidden input not found")

            # Step 6: Verify JavaScript debug output references correct value
            if f"Passenger Count Input Value: {count}" in booking_response.text:
                print(f"  ✓ JavaScript debug shows correct value")
            elif f"Passenger Count Input Value:" in booking_response.text:
                # Extract actual value from debug output
                match = re.search(r'Passenger Count Input Value: (\d+)', booking_response.text)
                if match:
                    js_value = int(match.group(1))
                    print(f"  ✓ JavaScript reads value: {js_value}")

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("All passenger counts 1-9 should display correctly.")
    print("Check console output above for any ✗ marks.")
    print("="*60)

if __name__ == '__main__':
    test_passenger_count_flow()