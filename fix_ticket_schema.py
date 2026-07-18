"""Fix tickets table schema to add missing columns."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.user import get_db_connection

def fix_tickets_table():
    """Add missing columns to tickets table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check current columns
        cursor.execute("DESCRIBE tickets")
        columns = [row[0] for row in cursor.fetchall()]
        
        print("Current tickets table columns:", columns)
        
        # Add passenger_id if missing
        if 'passenger_id' not in columns:
            print("\nAdding passenger_id column...")
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN passenger_id INT DEFAULT NULL,
                ADD CONSTRAINT fk_tickets_passenger 
                FOREIGN KEY (passenger_id) REFERENCES passengers(id)
                ON UPDATE CASCADE ON DELETE RESTRICT
            """)
            conn.commit()
            print("✓ passenger_id column added")
        else:
            print("✓ passenger_id column exists")
        
        # Add qr_code if missing
        if 'qr_code' not in columns:
            print("\nAdding qr_code column...")
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN qr_code TEXT DEFAULT NULL
            """)
            conn.commit()
            print("✓ qr_code column added")
        else:
            print("✓ qr_code column exists")
        
        print("\n✓ Schema fix completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Error fixing schema: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = fix_tickets_table()
    sys.exit(0 if success else 1)