"""
Test to identify the exact root cause of passenger_count always being 1.
"""

print("=== ROOT CAUSE ANALYSIS ===\n")

print("Issue traced through the code flow:\n")

print("1. search_flights.html line 136:")
print("   <input type='number' name='passenger_count' value='{{ request.form.get('passenger_count', 1) }}' />")
print("   ✓ User can select passenger count\n")

print("2. search_flights.html lines 236-241:")
print("   <a href='{{ url_for('user.book_flight', flight_id=flight.id, passenger_count=passenger_count) }}' class='btn btn-primary'>")
print("   ✓ Passes passenger_count in URL parameter\n")

print("3. routes/user.py line 140:")
print("   passenger_count = int(request.args.get('passenger_count', 1))")
print("   ✓ Receives passenger_count from URL on GET request\n")

print("4. routes/user.py line 180:")
print("   return render_template('book_flight.html', ..., passenger_count=passenger_count)")
print("   ✓ Passes to template\n")

print("5. book_flight.html line 60:")
print("   <input type='hidden' name='passenger_count' value='{{ passenger_count }}'>")
print("   ✓ Has hidden input with correct value\n")

print("6. book_flight.html lines 161-162:")
print("   const passengerCountInput = document.querySelector('input[name=\"passenger_count\"]');")
print("   ⚠️  This selects the HIDDEN input!")
print("   ⚠️  Hidden inputs cannot be changed by users!\n")

print("7. book_flight.html lines 224-226:")
print("   passengerCountInput.addEventListener('change', function() { ... })")
print("   ⚠️  Change event on hidden input NEVER FIRES!\n")

print("\n=== ROOT CAUSE IDENTIFIED ===")
print("File: book_flight.html")
print("Lines: 161-226")
print("")
print("The JavaScript selects the HIDDEN input field for passenger_count.")
print("Since it's hidden, the user cannot change it.")
print("The change event listener never fires.")
print("The passenger forms are generated ONCE on page load with the initial value.")
print("")
print("When the template variable {{ passenger_count }} is rendered by Jinja2,")
print("it shows the CORRECT value (e.g., 4) on page load.")
print("")
print("BUT: JavaScript reads from the hidden input which has the value '1'")
print("      or whatever was in the form field when rendered.")