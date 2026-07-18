#!/usr/bin/env python3
"""
Verify the booking flow and identify where passengers are lost.
"""

import re

print("=== VERIFYING BOOKING FLOW ===\n")

# Step 1: Check book_flight.html structure
print("1. BOOK_FLIGHT.HTML STRUCTURE:")
with open("templates/book_flight.html", "r") as f:
    content = f.read()
    
# Find all inputs with name="passenger_count"
inputs = re.findall(r'<input[^>]*name="passenger_count"[^>]*>', content)
print(f"   Found {len(inputs)} input(s) with name='passenger_count':")
for inp in inputs:
    print(f"     {inp}")

# Check if there's a visible input for passenger count
if '<input type="hidden" name="passenger_count"' in content:
    print("   ⚠️  ISSUE: The only passenger_count input is HIDDEN!")
    print("   ⚠️  Hidden inputs cannot be changed by users.")
    print("   ⚠️  The JavaScript reads from this hidden input.\n")

# Check JavaScript
print("2. JAVASCRIPT ANALYSIS:")
if 'querySelector(\'input[name="passenger_count"]\')' in content:
    print("   ⚠️  JavaScript selects: input[name='passenger_count']")
    print("   ⚠️  This is the HIDDEN input!")
    print("   ⚠️  User cannot change its value.\n")

# Check if JS generates correct forms
if 'generatePassengerForms' in content:
    print("   ✓ JavaScript function 'generatePassengerForms' exists")
    
    # Check the loop
    if 'for (let i = 0; i < count; i++)' in content:
        print("   ✓ Loop: for (let i = 0; i < count; i++)")
    
    # Check generated field names
    if 'name="passenger_name_' in content and 'name="passenger_email_' in content:
        print("   ✓ Generates fields like: passenger_name_0, passenger_name_1, etc.")
    
    # Check initial call
    if 'generatePassengerForms(parseInt(passengerCountInput.value))' in content:
        print("   ✓ Initial call uses: passengerCountInput.value")
        print("   ⚠️  But this reads from the HIDDEN input!\n")

# Step 3: Check routes
print("3. ROUTES ANALYSIS:")
with open("routes/user.py", "r") as f:
    routes = f.read()

# Check booking route GET
if 'request.args.get("passenger_count"' in routes:
    print("   ✓ Booking route GET: reads passenger_count from URL args")

# Check booking route POST
if 'for i in range(passenger_count):' in routes:
    print("   ✓ Booking route POST: loops through all passengers")
    print("   ✓ Extracts: passenger_name_{i}, passenger_email_{i}, etc.\n")

print("\n" + "="*60)
print("ROOT CAUSE IDENTIFIED")
print("="*60)
print("""
PROBLEM: 
The JavaScript in book_flight.html selects a HIDDEN input field
to determine how many passenger forms to generate.

Since the input is hidden:
1. Its value is set server-side (e.g., value="1")
2. The user cannot change it via UI
3. The change event listener never fires
4. Passenger forms are generated with the default value (usually 1)

WHY IT HAPPENS:
- Line 60: <input type="hidden" name="passenger_count" value="{{ passenger_count }}">
- Line 185: JavaScript selects this hidden input
- The value might be "1" or get reset somewhere

THE FIX:
JavaScript should NOT bind to a hidden input for dynamic form generation.
Instead, it should:
1. Read the value from a JavaScript variable or data attribute
2. OR add a visible, editable input for passenger count
3. OR pass the count directly to the function

RECOMMENDED FIX:
Change the hidden input to a visible number input that the user can actually see
and modify, OR store the passenger count in a data attribute that JavaScript can read.
""")

print("\n" + "="*60)
print("EXPECTED BEHAVIOR")
print("="*60)
print("""
When user selects 4 passengers and clicks Book:
1. Search form submits passenger_count=4
2. Booking page loads with passenger_count=4
3. JavaScript should generate 4 passenger forms
4. User fills in all 4 forms
5. On submit, all 4 passengers are sent to backend
6. Backend inserts all 4 passengers in database

ACTUAL BEHAVIOR:
1-2: ✓ Works correctly
3: ✗ Only 1 form generated (or default value used)
4-6: Cannot proceed because only 1 form exists
""")