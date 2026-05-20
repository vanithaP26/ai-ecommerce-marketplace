import os
import sys
from models.db_manager import DatabaseManager

def main():
    print("[TEST SUITE] Initializing testing suite...")
    
    # 1. Clean old test database if SQLite
    db_path = "database.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"[TEST SUITE] Cleared existing database: {db_path}")
        except Exception as e:
            print(f"[TEST SUITE WARNING] Could not remove old db: {e}")
            
    # 2. Database manager instantiation and auto-initialization
    try:
        db = DatabaseManager()
        print("[TEST SUITE] DatabaseManager instantiated successfully.")
    except Exception as e:
        print(f"[TEST SUITE ERROR] Failed to instantiate DatabaseManager: {e}")
        sys.exit(1)
        
    # 3. Verify Table Creation
    required_tables = ["users", "vendors", "categories", "products", "cart", "orders", "order_items", "reviews", "payments", "analytics_logs", "wishlist"]
    tables_result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
    created_tables = [r['name'] for r in tables_result]
    
    print(f"[TEST SUITE] Existing tables: {created_tables}")
    for table in required_tables:
        if table in created_tables:
            print(f"[TEST SUITE PASS] Table '{table}' verified.")
        else:
            print(f"[TEST SUITE FAIL] Table '{table}' is missing!")
            sys.exit(1)
            
    # 4. Verify seeding via Flask App Initialization
    try:
        from app import create_app
        app = create_app()
        print("[TEST SUITE] Flask App Factory executed successfully.")
    except Exception as e:
        print(f"[TEST SUITE ERROR] App Factory failed: {e}")
        sys.exit(1)
        
    # 5. Check if seeded accounts exist
    admin_users = db.execute_query("SELECT * FROM users WHERE role = 'admin'")
    if admin_users and len(admin_users) > 0:
        print(f"[TEST SUITE PASS] Admin account seeded: {admin_users[0]['username']} ({admin_users[0]['email']})")
    else:
        print("[TEST SUITE FAIL] Admin account seeding failed!")
        sys.exit(1)
        
    vendor_users = db.execute_query("SELECT * FROM vendors")
    if vendor_users and len(vendor_users) > 0:
        print(f"[TEST SUITE PASS] Vendor account seeded: {vendor_users[0]['business_name']}")
    else:
        print("[TEST SUITE FAIL] Vendor account seeding failed!")
        sys.exit(1)
        
    products = db.execute_query("SELECT * FROM products")
    if products and len(products) > 0:
        print(f"[TEST SUITE PASS] Product items seeded: {len(products)} found.")
    else:
        print("[TEST SUITE FAIL] Product seeding failed!")
        sys.exit(1)
        
    print("[TEST SUITE] All core test checks completed successfully!")

if __name__ == "__main__":
    main()
