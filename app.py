import os
from flask import Flask, render_template, session
from config import Config
from models.db_manager import DatabaseManager

# Import Blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.vendor import vendor_bp
from routes.admin import admin_bp
from routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure static upload folders exist
    Config.get_upload_path()
    
    # Initialize Database and seed tables
    db = DatabaseManager()
    
    # Seed default admin if missing
    _seed_default_admin(db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # Context Processor: Inject variables into templates
    @app.context_processor
    def inject_global_data():
        categories = []
        cart_count = 0
        try:
            categories = db.execute_query("SELECT * FROM categories", cache=True)
            
            # Count cart items if customer logged in
            user_id = session.get('user_id')
            if user_id and session.get('role') == 'customer':
                res = db.execute_query("SELECT SUM(quantity) as total_qty FROM cart WHERE user_id = %s", [user_id])
                if res and res[0]['total_qty']:
                    cart_count = res[0]['total_qty']
        except Exception as e:
            print(f"[CONTEXT PROCESSOR ERROR] {e}")
            
        return {
            'global_categories': categories,
            'global_cart_count': cart_count,
            'current_year': 2026
        }
        
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
        
    # Teardown database connection
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        # DatabaseManager is a singleton, connection remains open, 
        # but we could close it if desired. Leaving open for pool performance.
        pass
        
    return app

def _seed_default_admin(db_mgr):
    """Creates a default admin user and vendor test accounts if not already in system."""
    try:
        admin_exists = db_mgr.execute_query("SELECT id FROM users WHERE role = 'admin'")
        if not admin_exists:
            from utils.helpers import hash_password
            admin_pw_hash = hash_password('admin123')
            db_mgr.execute_non_query(
                "INSERT INTO users (username, email, password_hash, role, status) "
                "VALUES ('admin', 'admin@nexusmarket.com', %s, 'admin', 'active')",
                [admin_pw_hash]
            )
            print("[DATABASE SEED] Default admin account seeded: admin@nexusmarket.com / admin123")
            
            # Let's seed a test vendor as well for easy testing!
            vendor_pw_hash = hash_password('vendor123')
            v_user_id = db_mgr.execute_non_query(
                "INSERT INTO users (username, email, password_hash, role, status) "
                "VALUES ('techvendor', 'vendor@tech.com', %s, 'vendor', 'active')",
                [vendor_pw_hash]
            )
            db_mgr.execute_non_query(
                "INSERT INTO vendors (user_id, business_name, description, status, rating) "
                "VALUES (%s, 'Gizmo Tech Store', 'Your premier vendor for smartphones, smart home tools, and notebooks.', 'approved', 4.5)",
                [v_user_id]
            )
            
            # Let's seed a second pending vendor to demonstrate approvals
            pending_pw_hash = hash_password('vendor123')
            pv_user_id = db_mgr.execute_non_query(
                "INSERT INTO users (username, email, password_hash, role, status) "
                "VALUES ('fashionshop', 'vendor@fashion.com', %s, 'vendor', 'active')",
                [pending_pw_hash]
            )
            db_mgr.execute_non_query(
                "INSERT INTO vendors (user_id, business_name, description, status, rating) "
                "VALUES (%s, 'Vogue Outfitters', 'Boutique collection of modern apparel and premium watches.', 'pending', 0.0)",
                [pv_user_id]
            )
            
            # Let's seed some initial products for Gizmo Tech Store
            vendor_id = db_mgr.execute_query("SELECT id FROM vendors WHERE business_name = 'Gizmo Tech Store'")[0]['id']
            
            # Find category IDs
            electronics_id = db_mgr.execute_query("SELECT id FROM categories WHERE slug = 'electronics'")[0]['id']
            home_id = db_mgr.execute_query("SELECT id FROM categories WHERE slug = 'home-kitchen'")[0]['id']
            
            db_mgr.execute_non_query(
                "INSERT INTO products (vendor_id, category_id, name, description, price, stock, image_url, status, average_rating) "
                "VALUES "
                "(%s, %s, 'Titan Smart Watch X', 'Cutting edge smartwatch with OLED display, GPS track, blood oxygen logs and 7-day battery.', 199.99, 25, 'uploads/products/watch.jpg', 'active', 4.8),"
                "(%s, %s, 'Nexus Pro Wireless Earbuds', 'Noise cancelling bluetooth 5.2 earbuds with deep bass and charging case.', 89.95, 4, 'uploads/products/earbuds.jpg', 'active', 4.5),"
                "(%s, %s, 'AeroBook Pro 15', 'Super slim 15.6 inch laptop with 16GB RAM, 512GB SSD, Intel Core i7 processor.', 899.00, 12, 'uploads/products/laptop.jpg', 'active', 4.7),"
                "(%s, %s, 'Smart Thermostat Hub', 'Smart home climate hub supporting voice control and energy optimization schedules.', 129.00, 0, 'uploads/products/thermostat.jpg', 'active', 4.2)",
                [vendor_id, electronics_id, vendor_id, electronics_id, vendor_id, electronics_id, vendor_id, home_id]
            )
            print("[DATABASE SEED] Sample products and vendor accounts successfully seeded.")
    except Exception as e:
        print(f"[DATABASE SEED ERROR] Failed to seed default data: {e}")

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
