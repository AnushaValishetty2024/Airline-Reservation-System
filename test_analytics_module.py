"""Test analytics module functionality."""
from services.analytics_service import analytics_service

print("=" * 60)
print("Testing Analytics Module")
print("=" * 60)

# Test 1: Dashboard KPIs
print("\n1. Testing get_dashboard_kpis()...")
try:
    kpis = analytics_service.get_dashboard_kpis()
    print(f"   Total Revenue: ₹{kpis.get('total_revenue', 0):.2f}")
    print(f"   Total Bookings: {kpis.get('total_bookings', 0)}")
    print(f"   Total Flights: {kpis.get('total_flights', 0)}")
    print(f"   Total Airlines: {kpis.get('total_airlines', 0)}")
    print(f"   Total Customers: {kpis.get('total_customers', 0)}")
    print(f"   Today's Revenue: ₹{kpis.get('today_revenue', 0):.2f}")
    print(f"   Today's Bookings: {kpis.get('today_bookings', 0)}")
    print(f"   Avg Booking Value: ₹{kpis.get('avg_booking_value', 0):.2f}")
    print(f"   Avg Occupancy Rate: {kpis.get('avg_occupancy', 0):.1f}%")
    print("   ✓ KPIs retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Revenue Trends
print("\n2. Testing get_revenue_trends()...")
try:
    trends = analytics_service.get_revenue_trends(days=7)
    print(f"   Retrieved {len(trends)} days of revenue data")
    if trends:
        print(f"   Sample: {trends[0]}")
    print("   ✓ Revenue trends retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Monthly Revenue
print("\n3. Testing get_monthly_revenue()...")
try:
    monthly = analytics_service.get_monthly_revenue(months=6)
    print(f"   Retrieved {len(monthly)} months of revenue data")
    if monthly:
        print(f"   Sample: {monthly[0]}")
    print("   ✓ Monthly revenue retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Booking Trends
print("\n4. Testing get_booking_trends()...")
try:
    booking_trends = analytics_service.get_booking_trends(months=6)
    print(f"   Retrieved {len(booking_trends)} months of booking data")
    if booking_trends:
        print(f"   Sample: {booking_trends[0]}")
    print("   ✓ Booking trends retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Booking Status Distribution
print("\n5. Testing get_booking_status_distribution()...")
try:
    status_dist = analytics_service.get_booking_status_distribution()
    print(f"   Status distribution: {status_dist}")
    print("   ✓ Booking status distribution retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Top Airlines
print("\n6. Testing get_top_airlines_by_revenue()...")
try:
    top_airlines = analytics_service.get_top_airlines_by_revenue(limit=5)
    print(f"   Retrieved {len(top_airlines)} top airlines")
    if top_airlines:
        print(f"   Top airline: {top_airlines[0].get('airline_name')} - ₹{top_airlines[0].get('total_revenue', 0):.2f}")
    print("   ✓ Top airlines retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 7: Top Routes
print("\n7. Testing get_top_routes_by_bookings()...")
try:
    top_routes = analytics_service.get_top_routes_by_bookings(limit=5)
    print(f"   Retrieved {len(top_routes)} top routes")
    if top_routes:
        print(f"   Top route: {top_routes[0].get('route_name')} - {top_routes[0].get('total_bookings')} bookings")
    print("   ✓ Top routes retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 8: Top Flights
print("\n8. Testing get_top_flights_by_occupancy()...")
try:
    top_flights = analytics_service.get_top_flights_by_occupancy(limit=5)
    print(f"   Retrieved {len(top_flights)} top flights")
    if top_flights:
        print(f"   Top flight: {top_flights[0].get('flight_number')} - {top_flights[0].get('occupancy_rate')}% occupancy")
    print("   ✓ Top flights retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 9: Customer Insights
print("\n9. Testing get_customer_insights()...")
try:
    customers = analytics_service.get_customer_insights(limit=5)
    print(f"   Retrieved {len(customers)} top customers")
    if customers:
        print(f"   Top customer: {customers[0].get('full_name')} - ₹{customers[0].get('total_spent', 0):.2f}")
    print("   ✓ Customer insights retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 10: Payment Method Distribution
print("\n10. Testing get_payment_method_distribution()...")
try:
    payment_dist = analytics_service.get_payment_method_distribution()
    print(f"   Payment methods: {payment_dist}")
    print("   ✓ Payment method distribution retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 11: Airline Distribution
print("\n11. Testing get_airline_distribution()...")
try:
    airline_dist = analytics_service.get_airline_distribution()
    print(f"   Airlines: {airline_dist}")
    print("   ✓ Airline distribution retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 12: Weekly Revenue
print("\n12. Testing get_weekly_revenue()...")
try:
    weekly = analytics_service.get_weekly_revenue(weeks=4)
    print(f"   Retrieved {len(weekly)} weeks of revenue data")
    if weekly:
        print(f"   Sample: {weekly[0]}")
    print("   ✓ Weekly revenue retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 13: Hourly Booking Distribution
print("\n13. Testing get_hourly_booking_distribution()...")
try:
    hourly = analytics_service.get_hourly_booking_distribution()
    print(f"   Retrieved {len(hourly)} hour slots")
    if hourly:
        print(f"   Peak hour sample: {hourly[0]}")
    print("   ✓ Hourly booking distribution retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 14: Aircraft Utilization
print("\n14. Testing get_aircraft_utilization()...")
try:
    aircraft = analytics_service.get_aircraft_utilization()
    print(f"   Retrieved {len(aircraft)} aircraft types")
    if aircraft:
        print(f"   Sample: {aircraft[0]}")
    print("   ✓ Aircraft utilization retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 15: Revenue by Payment Method
print("\n15. Testing get_revenue_by_payment_method()...")
try:
    rev_by_pm = analytics_service.get_revenue_by_payment_method(months=3)
    print(f"   Retrieved {len(rev_by_pm)} records")
    if rev_by_pm:
        print(f"   Sample: {rev_by_pm[0]}")
    print("   ✓ Revenue by payment method retrieved successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Analytics Module Testing Complete!")
print("=" * 60)