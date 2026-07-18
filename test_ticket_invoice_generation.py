"""
Test to verify that tickets and invoices are generated automatically after payment.
This test verifies the fix for the issue where booking history showed:
- Boarding Pass: "Ticket not available"
- Invoice: "Invoice not available"
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from models.user import get_db_connection
from models.booking import create_booking
from services.payment_service import process_payment
from services.ticket_service import get_ticket_path, create_ticket
from services.invoice_service import get_invoice_path, create_invoice


def test_complete_flow():
    """Test the complete flow: booking -> payment -> ticket -> invoice"""
    
    print("=" * 80)
    print("TESTING COMPLETE BOOKING FLOW")
    print("=" * 80)
    
    with app.app_context():
        # Use test database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get a test user
            cursor.execute("SELECT id, email FROM users LIMIT 1")
            user = cursor.fetchone()
            if not user:
                print("❌ No test user found. Please run seed_users.py first.")
                return False
            
            print(f"\n✓ Using test user: {user['email']} (ID: {user['id']})")
            
            # Get a test flight and reset seat count
            cursor.execute("""
                SELECT f.id, f.flight_number, f.economy_price, f.departure_datetime, f.arrival_datetime
                FROM flights f
                LIMIT 1
            """)
            flight = cursor.fetchone()
            if not flight:
                print("❌ No test flight found. Please run seed_db.py first.")
                return False
            
            # Reset flight seats for testing
            cursor.execute("UPDATE flights SET seats_economy = 100, seats_business = 20 WHERE id = %s", (flight['id'],))
            conn.commit()
            
            print(f"✓ Using test flight: {flight['flight_number']} (ID: {flight['id']})")
            
            # Create a test booking
            print("\n" + "-" * 80)
            print("STEP 1: Creating Booking")
            print("-" * 80)
            
            passengers_data = [
                {
                    "name": "Test Passenger",
                    "email": "test@example.com",
                    "mobile": "1234567890",
                    "passport": "A12345678",
                    "gender": "Male",
                    "dob": "1990-01-01",
                    "seat_number": "12A"
                }
            ]
            
            booking_id = create_booking(
                user_id=user['id'],
                flight_id=flight['id'],
                passengers_data=passengers_data,
                seat_class="economy",
                total_amount=float(flight['economy_price'])
            )
            
            print(f"✓ Booking created successfully (ID: {booking_id})")
            
            # Process payment
            print("\n" + "-" * 80)
            print("STEP 2: Processing Payment")
            print("-" * 80)
            
            amount = flight['economy_price']
            payment_method = "Credit Card"
            
            payment_result = process_payment(booking_id, amount, payment_method)
            
            if not payment_result.get('success'):
                print(f"❌ Payment failed: {payment_result.get('error', 'Unknown error')}")
                return False
            
            print(f"✓ Payment successful (Reference: {payment_result.get('payment_reference')})")
            print(f"  Transaction ID: {payment_result.get('transaction_id')}")
            print(f"  Amount: ₹{payment_result.get('amount')}")
            
            # Check if ticket was created
            print("\n" + "-" * 80)
            print("STEP 3: Verifying Ticket Generation")
            print("-" * 80)
            
            ticket_path = get_ticket_path(booking_id)
            if ticket_path and os.path.exists(ticket_path):
                print(f"✓ Ticket PDF generated: {ticket_path}")
            else:
                print(f"❌ Ticket NOT generated (Path: {ticket_path})")
                return False
            
            # Check if invoice was created
            print("\n" + "-" * 80)
            print("STEP 4: Verifying Invoice Generation")
            print("-" * 80)
            
            invoice_path = get_invoice_path(booking_id)
            if invoice_path and os.path.exists(invoice_path):
                print(f"✓ Invoice PDF generated: {invoice_path}")
            else:
                print(f"❌ Invoice NOT generated (Path: {invoice_path})")
                return False
            
            # Verify database records
            print("\n" + "-" * 80)
            print("STEP 5: Verifying Database Records")
            print("-" * 80)
            
            cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE booking_id = %s", (booking_id,))
            ticket_count = cursor.fetchone()['count']
            print(f"✓ Ticket records in DB: {ticket_count}")
            
            cursor.execute("SELECT COUNT(*) as count FROM invoices WHERE booking_id = %s", (booking_id,))
            invoice_count = cursor.fetchone()['count']
            print(f"✓ Invoice records in DB: {invoice_count}")
            
            if ticket_count == 0 or invoice_count == 0:
                print("❌ Missing database records")
                return False
            
            print("\n" + "=" * 80)
            print("✅ ALL CHECKS PASSED!")
            print("=" * 80)
            print("\nSUMMARY:")
            print(f"  • Booking ID: {booking_id}")
            print(f"  • Ticket PDF: {ticket_path}")
            print(f"  • Invoice PDF: {invoice_path}")
            print(f"  • Ticket DB records: {ticket_count}")
            print(f"  • Invoice DB records: {invoice_count}")
            print("\n" + "=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Cleanup
            try:
                # Delete test data to keep DB clean
                cursor.execute("DELETE FROM tickets WHERE booking_id = %s", (booking_id,))
                cursor.execute("DELETE FROM invoices WHERE booking_id = %s", (booking_id,))
                cursor.execute("DELETE FROM booking_passengers WHERE booking_id = %s", (booking_id,))
                cursor.execute("DELETE FROM payments WHERE booking_id = %s", (booking_id,))
                cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
                cursor.execute("DELETE FROM passengers WHERE email = 'test@example.com'")
                conn.commit()
                print(f"\n✓ Cleaned up test data (Booking ID: {booking_id})")
            except:
                pass
            
            cursor.close()
            conn.close()


if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)