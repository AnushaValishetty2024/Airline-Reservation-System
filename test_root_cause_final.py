#!/usr/bin/env python3
"""
Final root cause identification.
"""

print("=== TRACING THE COMPLETE FLOW ===\n")

with open("routes/user.py", "r") as f:
    user_routes = f.read()

with open("templates/search_flights.html", "r") as f:
    search_html = f.read()

print("STEP 1: Search route initialization")
lines = user_routes.split('\n')
for i, line in enumerate(lines, 1):
    if i >= 55 and i <= 65:
        print(f"Line {i}: {line}")

print("\nSTEP 2: Search route POST handling")
for i, line in enumerate(lines, 1):
    if i >= 75 and i <= 80:
        print(f"Line {i}: {line}")

print("\nSTEP 3: Search route render")
for i, line in enumerate(lines, 1):
    if i >= 89 and i <= 96:
        print(f"Line {i}: {line}")

print("\nSTEP 4: Book button in search_flights.html")
search_lines = search_html.split('\n')
for i, line in enumerate(search_lines, 1):
    if i >= 236 and i <= 244:
        print(f"Line {i}: {line}")

print("\n" + "="*60)
print("CRITICAL FINDING")
print("="*60)
print("""
In search_flights.html line 238:
    passenger_count=passenger_count

This uses the Jinja2 variable `passenger_count` from the server-side render.

In routes/user.py, line 75:
    passenger_count = request.form.get("passenger_count", 1, type=int)

This reads from the POST data when the search form is submitted.

If the user enters 4 passengers and searches:
1. Form submits passenger_count=4
2. Route reads it as passenger_count = 4
3. Route passes to template as passenger_count=4
4. Template renders: passenger_count=passenger_count → 4
5. Book button URL: ?passenger_count=4
6. Booking route receives 4
7. Template displays Passenger Count = 4

This SHOULD work... unless:

HYPOTHESIS: The search form is submitting but passenger_count is NOT
being sent in the POST data, OR the form field has a different name,
OR there's a JavaScript issue preventing the value update.
""")

print("Checking search form field name...")
for i, line in enumerate(search_lines, 1):
    if 'passenger_count' in line and 'name=' in line:
        print(f"Line {i}: {line.rstrip()}")