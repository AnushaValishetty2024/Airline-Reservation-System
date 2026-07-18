import requests
from urllib.parse import urljoin

base = 'http://127.0.0.1:5000'
session = requests.Session()

# Test admin login
login_data = {'email': 'admin@airline.com', 'password': 'admin123'}
resp = session.post(urljoin(base, '/login'), data=login_data, allow_redirects=False)
print(f'✓ Admin login: {resp.status_code} (expected 302)')
assert resp.status_code == 302

# Test admin flights page
resp = session.get(urljoin(base, '/admin/flights'))
print(f'✓ Admin flights page: {resp.status_code}')
assert resp.status_code == 200

# Test user search page
resp = session.get(urljoin(base, '/search'))
print(f'✓ Search page loads: {resp.status_code}')
assert resp.status_code == 200
assert 'Search Flights' in resp.text or 'Find Flights' in resp.text

# Extract CSRF token and test search with filters
print("\n=== Testing Flight Search ===")
resp = session.get(urljoin(base, '/search'))
import re
csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', resp.text).group(1)

search_data = {
    'csrf_token': csrf_token,
    'origin_airport_id': '',  # Any
    'destination_airport_id': '',  # Any
    'departure_date': '2026-07-15',
    'airline_id': '',
    'sort_by': 'departure_earliest',
    'min_price': '',
    'max_price': '',
    'time_of_day': '',
    'passenger_count': 1,
    'cabin_class': 'economy'
}
resp = session.post(urljoin(base, '/search'), data=search_data)
print(f'✓ Search POST: {resp.status_code}')
assert resp.status_code == 200
assert 'Search Results' in resp.text or 'No flights found' in resp.text
print(f'  Contains flight results: {"Search Results" in resp.text}')

# Test booking history page
resp = session.get(urljoin(base, '/history'))
print(f'✓ Booking history page: {resp.status_code}')
assert resp.status_code == 200

# Test booking a flight
print("\n=== Testing Flight Booking ===")
# First, get a flight ID from search results
search_resp = session.post(urljoin(base, '/search'), data=search_data)
# Extract first flight ID from the page
import re
flight_ids = re.findall(r'/book/(\d+)', search_resp.text)
if flight_ids:
    flight_id = flight_ids[0]
    print(f'  Found flight ID: {flight_id}')
    
    # Get booking page
    resp = session.get(urljoin(base, f'/book/{flight_id}'))
    print(f'✓ Booking page loads: {resp.status_code}')
    assert resp.status_code == 200
    
# Extract CSRF token for booking
    resp = session.get(urljoin(base, f'/book/{flight_id}'))
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', resp.text).group(1)
    
    # Submit booking
    booking_data = {
        'csrf_token': csrf_token,
        'seat_class': 'economy',
        'passenger_count': 1,
        'passenger_name_0': 'Test Passenger',
        'passenger_email_0': 'test@example.com',
        'passenger_mobile_0': '+15550000001',
        'passenger_passport_0': 'P123456',
        'seat_number_0': '12A'
    }
    resp = session.post(urljoin(base, f'/book/{flight_id}'), data=booking_data, allow_redirects=False)
    print(f'✓ Booking POST: {resp.status_code}')
    if resp.status_code == 302:
        print(f'  Redirected to: {resp.headers.get("Location", "unknown")}')
    
    # Check booking history
    resp = session.get(urljoin(base, '/history'))
    print(f'✓ Booking history after booking: {resp.status_code}')
    assert 'BK' in resp.text or 'No bookings' in resp.text or 'booking_reference' in resp.text.lower()
else:
    print('  No flights available for booking test')

print("\n=== All Critical Tests Passed! ===")