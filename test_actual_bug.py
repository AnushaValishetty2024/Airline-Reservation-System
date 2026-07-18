#!/usr/bin/env python3
"""
Test to identify the EXACT root cause by simulating the actual flow.
"""

print("=== SIMULATING THE ACTUAL FLOW ===\n")

# Step 1: Check book_flight.html JavaScript
print("1. EXAMINING book_flight.html JAVASCRIPT:")
with open("templates/book_flight.html", "r") as f:
    lines = f.readlines()
    
for i in range(159, 228):
    print(f"Line {i+1}: {lines[i].rstrip()}")

print("\n" + "="*60)
print("ROOT CAUSE ANALYSIS")
print("="*60)
print("""
The JavaScript selects: input[name="passenger_count"]
At line 161: const passengerCountInput = document.querySelector('input[name="passenger_count"]');

This will select the FIRST input with name="passenger_count".

In the HTML at line 60, there's a hidden input:
Input 1: <input type="hidden" name="passenger_count" value="{{ passenger_count }}">

If the JavaScript reads value="..." on page load from the hidden input,
it should get the correct value... unless...

WAIT! Let me check if there's ANOTHER passenger_count input that appears
AFTER the hidden input in the DOM.

The JavaScript might be selecting the WRONG input or there might be
a conflict.

Let me search for ALL inputs with name="passenger_count" in book_flight.html
""")

with open("templates/book_flight.html", "r") as f:
    content = f.read()

import re
inputs = re.findall(r'<input[^>]*name="passenger_count"[^>]*>', content)
print(f"\nFound {len(inputs)} input(s) with name='passenger_count':")
for inp in inputs:
    print(f"  {inp}")

print("""
IF there are multiple inputs:
- querySelector returns the FIRST match
- If the first match has value="" or value="1", that's what JavaScript reads
- This would cause the bug!

HYPOTHESIS:
There might be another passenger_count input field that appears BEFORE
the hidden input in the DOM order, causing JavaScript to read the wrong value.
""")