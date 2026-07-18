#!/usr/bin/env python3
"""
Comprehensive debugging to find why passenger_count is always 1.
"""
import re

def analyze_file(filepath, label):
    print(f"\n{'='*60}")
    print(f"ANALYZING: {label}")
    print(f"File: {filepath}")
    print('='*60)
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if 'passenger_count' in line.lower():
            print(f"Line {i}: {line.rstrip()}")

# Analyze all key files
analyze_file("templates/search_flights.html", "Search Flights Template")
analyze_file("templates/book_flight.html", "Book Flight Template")
analyze_file("routes/user.py", "User Routes")

print("\n" + "="*60)
print("ANALYSIS SUMMARY")
print("="*60)

# Check the key flow
with open("templates/book_flight.html", "r") as f:
    book_html = f.read()

with open("routes/user.py", "r") as f:
    user_routes = f.read()

print("\n1. Does book_flight.html have a HIDDEN input for passenger_count?")
if 'type="hidden"' in book_html and 'passenger_count' in book_html:
    # Find the line
    for i, line in enumerate(book_html.split('\n'), 1):
        if 'type="hidden"' in line and 'passenger_count' in line:
            print(f"   YES - Line {i}: {line.strip()}")
            break
else:
    print("   NO")

print("\n2. Does JavaScript select input[name='passenger_count']?")
if 'querySelector' in book_html and 'passenger_count' in book_html:
    for i, line in enumerate(book_html.split('\n'), 1):
        if 'querySelector' in line and 'passenger_count' in line:
            print(f"   YES - Line {i}: {line.strip()}")
            break
else:
    print("   NO")

print("\n3. Does route GET /book/<id> read passenger_count from args?")
if 'request.args.get("passenger_count"' in user_routes:
    for i, line in enumerate(user_routes.split('\n'), 1):
        if 'request.args.get("passenger_count"' in line:
            print(f"   YES - Line {i}: {line.strip()}")
            break
else:
    print("   NO")

print("\n4. Does route POST /book/<id> read passenger_count from form?")
if 'request.form.get("passenger_count"' in user_routes:
    for i, line in enumerate(user_routes.split('\n'), 1):
        if 'request.form.get("passenger_count"' in line:
            print(f"   YES - Line {i}: {line.strip()}")
            break
else:
    print("   NO")

print("\n5. Is there a visible passenger_count input in book_flight.html?")
visible_inputs = re.findall(r'<input[^>]*name="passenger_count"[^>]*>', book_html)
if visible_inputs:
    for inp in visible_inputs:
        if 'type="hidden"' not in inp:
            print(f"   YES: {inp}")
        else:
            print(f"   HIDDEN: {inp}")
else:
    print("   NO INPUT FOUND")

print("\n6. Does book_flight.html read the hidden input value on page load?")
if 'parseInt(passengerCountInput.value)' in book_html:
    print("   YES - JavaScript reads value on load")
else:
    print("   NO")

print("\n" + "="*60)
print("ROOT CAUSE DETERMINATION")
print("="*60)

# The real issue
with open("book_flight.html", "r") as f:
    book_content = f.read()

# Check line 58 which displays passenger count
lines = book_content.split('\n')
for i, line in enumerate(lines, 1):
    if 'Passenger Count = ' in line:
        print(f"\nLine {i}: {line.strip()}")
        print("\nThis displays the value. If it always shows 1,")
        print("then passenger_count is being passed as 1 from the route.")

print("\n" + "="*60)
print("CHECKING ROUTE")
print("="*60)

lines_user = user_routes.split('\n')
for i, line in enumerate(lines_user, 1):
    if 135 <= i <= 145:
        print(f"Line {i}: {line}")