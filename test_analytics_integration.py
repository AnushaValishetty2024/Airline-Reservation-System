"""Test Day 6 Analytics Integration."""
import sys
import traceback

print("=" * 60)
print("DAY 6 ANALYTICS INTEGRATION TEST")
print("=" * 60)

# Test 1: Import app
print("\n[1] Testing app import...")
try:
    from app import app
    print("✓ App imported successfully")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check analytics blueprint
print("\n[2] Checking analytics blueprint registration...")
try:
    if 'analytics' in app.blueprints:
        analytics_bp = app.blueprints['analytics']
        print(f"✓ Analytics blueprint registered: {analytics_bp.name}")
    else:
        print("✗ Analytics blueprint NOT found")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error checking blueprints: {e}")
    sys.exit(1)

# Test 3: Check analytics routes
print("\n[3] Checking analytics routes...")
try:
    analytics_routes = [rule for rule in app.url_map.iter_rules() if 'analytics' in rule.rule]
    print(f"✓ Found {len(analytics_routes)} analytics routes:")
    for route in sorted(analytics_routes):
        print(f"  - {route.rule}")
except Exception as e:
    print(f"✗ Error checking routes: {e}")
    traceback.print_exc()

# Test 4: Check service import
print("\n[4] Testing BusinessAnalyticsService import...")
try:
    from services.business_analytics_service import BusinessAnalyticsService
    print("✓ BusinessAnalyticsService imported successfully")
except Exception as e:
    print(f"✗ Failed to import BusinessAnalyticsService: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check CSV exporter import
print("\n[5] Testing CSVExporter import...")
try:
    from utils.csv_exporter import CSVExporter
    print("✓ CSVExporter imported successfully")
except Exception as e:
    print(f"✗ Failed to import CSVExporter: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Check templates exist
print("\n[6] Checking analytics templates...")
import os
template_files = [
    'templates/admin/analytics.html',
    'templates/admin/analytics_dashboard.html',
    'templates/admin/analytics_revenue.html',
    'templates/admin/analytics_bookings.html',
    'templates/admin/analytics_customers.html',
    'templates/admin/analytics_routes.html',
    'templates/admin/analytics_flights.html',
    'templates/admin/analytics_occupancy.html',
    'templates/admin/analytics_payments.html',
    'templates/admin/analytics_cancellations.html',
    'templates/admin/analytics_destinations.html',
    'templates/admin/analytics_export.html',
]

missing = []
for template in template_files:
    if os.path.exists(template):
        print(f"  ✓ {template}")
    else:
        print(f"  ✗ {template} - MISSING")
        missing.append(template)

if missing:
    print(f"\n✗ Missing {len(missing)} templates")
else:
    print("\n✓ All templates present")

# Test 7: Check service methods
print("\n[7] Checking BusinessAnalyticsService methods...")
try:
    required_methods = [
        'get_executive_kpis',
        'get_revenue_analytics',
        'get_booking_analytics',
        'get_customer_analytics',
        'get_route_analytics',
        'get_flight_analytics',
        'get_occupancy_analytics',
        'get_payment_analytics',
        'get_cancellation_analytics',
        'get_destination_analytics',
        'get_top_customers_with_ranking',
        'export_analytics_data',
        'prepare_power_bi_datasets'
    ]
    
    service = BusinessAnalyticsService()
    missing_methods = []
    
    for method in required_methods:
        if hasattr(service, method):
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} - MISSING")
            missing_methods.append(method)
    
    service.close()
    
    if missing_methods:
        print(f"\n✗ Missing {len(missing_methods)} methods")
    else:
        print("\n✓ All required methods present")
        
except Exception as e:
    print(f"✗ Error checking methods: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE")
print("=" * 60)