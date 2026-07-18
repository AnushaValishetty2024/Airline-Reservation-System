import requests
from urllib.parse import urljoin

base = 'http://127.0.0.1:5000'
session = requests.Session()

# Test login with correct password
login_data = {'email': 'admin@airline.com', 'password': 'admin123'}
resp = session.post(urljoin(base, '/login'), data=login_data, allow_redirects=False)
print(f'Login status: {resp.status_code}, Redirect: {resp.headers.get("Location", "none")}')
print(f'Response contains error: {"Invalid email or password" in resp.text}')

if resp.status_code == 302:
    print('Login redirected!')
    # Test admin flights
    resp = session.get(urljoin(base, '/admin/flights'))
    print(f'Admin flights: {resp.status_code}')
    print(f'Contains airlines dropdown: {"airlines" in resp.text}')
    print(f'Contains airports dropdown: {"airports" in resp.text}')
    print(f'Contains aircraft dropdown: {"aircraft" in resp.text}')
    print(f'Has flight rows: {resp.text.count("data-id=")}')
else:
    # Check if login page shows error
    print('Login failed - check credentials')