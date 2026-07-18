"""
Manual test to trace passenger_count flow from search to booking.
Run this to see where the value is lost.
"""

# Test 1: Check search_flights.html book button
print("=== TEST 1: Book Button ===")
with open("templates/search_flights.html", "r") as f:
    content = f.read()
    if 'passenger_count=passenger_count' in content:
        print("✓ Book button uses passenger_count variable")
    else:
        print("✗ Book button does NOT use passenger_count variable")

# Test 2: Check book_flight.html receives passenger_count
print("\n=== TEST 2: book_flight.html Form ===")
with open("templates/book_flight.html", "r") as f:
    content = f.read()
    if 'passenger_count' in content:
        print("✓ book_flight.html mentions passenger_count")
    else:
        print("✗ book_flight.html missing passenger_count")

# Test 3: Check if JavaScript generates forms
print("\n=== TEST 3: JavaScript Form Generation ===")
with open("templates/book_flight.html", "r") as f:
    content = f.read()
    if 'generatePassengerForms' in content:
        print("✓ JavaScript passenger form generation exists")
    else:
        print("✗ JavaScript passenger form generation MISSING")

# Test 4: Check route handling
print("\n=== TEST 4: Route book_flight ===")
with open("routes/user.py", "r") as f:
    content = f.read()
    if 'passenger_count = int(request.form.get("passenger_count", 1))' in content:
        print("✓ Route reads passenger_count from POST form")
    else:
        print("✗ Route does NOT read passenger_count correctly")

# Test 5: Check if routes/user.py GET request gets passenger_count
print("\n=== TEST 5: GET request handling ===")
with open("routes/user.py", "r") as f:
    content = f.read()
    if 'request.args.get("passenger_count"' in content:
        print("✓ Route reads passenger_count from GET args")
    else:
        print("✗ Route does NOT read passenger_count from GET args")

print("\n=== SUMMARY ===")
print("The flow should be:")
print("1. User selects passenger_count in search_flights.html")
print("2. Clicks Book → URL includes ?passenger_count=N")
print("3. Route GET /book/<id> receives passenger_count from args")
print("4. Template displays N passenger forms via JavaScript")
print("5. User fills form and submits")
print("6. Route POST processes all passengers")