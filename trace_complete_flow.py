#!/usr/bin/env python3
"""
Trace the exact point where passenger_count gets lost.
"""

print("=== COMPLETE FLOW TRACE ===\n")

# 1. Check if search form submission properly passes passenger_count
print("1. SEARCH FORM FIELD:")
with open("templates/search_flights.html", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if 'name="passenger_count"' in line:
            print(f"   Line {i}: {line.strip()}")

# 2. Check if search route reads it properly
print("\n2. SEARCH ROUTE POST HANDLER:")
with open("routes/user.py", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if i == 75:
            print(f"   Line {i}: {line.strip()}")

# 3. Check if it's passed to template
print("\n3. ROUTE RENDER CALL:")
for i, line in enumerate(lines, 1):
    if i == 95:
        print(f"   Line {i}: {line.strip()}")

# 4. Check Book button
print("\n4. BOOK BUTTON:")
with open("templates/search_flights.html", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if 236 <= i <= 241:
            print(f"   Line {i}: {line.rstrip()}")

# 5. Check booking route GET
print("\n5. BOOKING ROUTE GET HANDLER:")
with open("routes/user.py", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if i == 140:
            print(f"   Line {i}: {line.strip()}")

# 6. Check booking template display
print("\n6. BOOKING TEMPLATE DISPLAY:")
with open("templates/book_flight.html", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if i == 58:
            print(f"   Line {i}: {line.strip()}")

print("\n" + "="*60)
print("CRITICAL QUESTION")
print("="*60)
print("""
When the SEARCH form is submitted with passenger_count=4, does the
route actually receive it?

The issue is: Line 61 in routes/user.py sets passenger_count = 1
BEFORE checking if request.method == "POST".

This means:
- On initial GET request: passenger_count = 1 ✓
- On POST request with passenger_count=4: passenger_count becomes 4 ✓
- Template gets passenger_count=4 ✓

But what if... the form submission is NOT including passenger_count?

OR... what if when the user changes the passenger count from 1 to 4,
and then clicks Search, the value is not being submitted?

Let me check the form field HTML more carefully.
""")

# Check if there's any JavaScript preventing form submission
print("\n7. CHECKING FOR FORM INTERFERENCE:")
with open("templates/search_flights.html", "r") as f:
    content = f.read()
    if 'submit' in content.lower() and 'passenger' in content.lower():
        print("   Found 'submit' and 'passenger' keywords")
    if '<script>' in content.lower():
        print("   Found inline script")
    else:
        print("   No inline scripts found")

print("\n" + "="*60)
print("HYPOTHESIS: THE ISSUE IS IN SEARCH_FLIGHTS.HTML")
print("="*60)
print("""
The search form submits via POST. The passenger_count input has:
    name="passenger_count"
    value="{{ request.form.get('passenger_count', 1) }}"

On GET (initial load), this shows value=1.
When user changes it to 4 and submits, it should send passenger_count=4.

BUT: If the value attribute is hardcoded to 1 somehow, or if there's
a Jinja2 rendering issue...

ACTUALLY WAIT!

I see it now! Let me check the template rendering pattern again.
""")

with open("templates/search_flights.html", "r") as f:
    content = f.read()
    import re
    pattern = r'value=\{\{ request\.form\.get\([^}]+\).*?\}\}'
    matches = re.findall(pattern, content)
    print("\nForm fields that use request.form.get:")
    for match in matches[:5]:
        print(f"   {match}")

print("\n" + "="*60)
print("ACTUAL ISSUE:")
print("="*60)
print("""
The input uses:
    value="{{ request.form.get('passenger_count', 1) }}"

On initial page load (GET request), request.form is empty.
So request.form.get('passenger_count', 1) returns the DEFAULT value 1.

When the form is submitted:
- If user changed the value to 4, the POST data has passenger_count=4
- The route reads it: request.form.get("passenger_count", 1, type=int)
- Passes to template
- Jinja2 renders: value="4"

BUT if there's a re-render or the form retains old values...

WAIT! I need to check if the form is actually submitting correctly.

Actually, looking at the problem statement again: "Booking page always displays
Passenger Count = 1"

This could be because:
1. The search form is not submitting passenger_count
2. The booking route is not receiving it
3. The booking template is not displaying it correctly

Given my analysis, I suspect the issue is in HOW the form field is rendered.
When the page first loads, request.form.get returns 1 (the default).
When the user submits the form, it should work...
UNLESS THE FORM IS NOT SUBMITTING THE VALUE.

Let me verify by looking at the search form structure ONE MORE TIME.
""")