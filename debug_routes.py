import requests
from urllib.parse import urljoin

base = 'http://127.0.0.1:5000'
session = requests.Session()

# Use the correct password from sample_data.sql
login_data = {'email': 'admin@airline.com', 'password': 'admin123'}
resp = session.post(urljoin(base, '/login'), data=login_data, allow_redirects=False)
print(f'Login status: {resp.status_code}')
print(f'Login redirect: {resp.headers.get("Location", "none")}')

# Get the actual HTML to see what's there
resp = session.get(urljoin(base, '/admin/flights'))
print(f'\nAdmin flights HTML length: {len(resp.text)}')
print('First 2000 chars:')
print(resp.text[:2000])