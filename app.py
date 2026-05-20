import os
import re
from flask import Flask, render_template, session
from config import Config
from models.db_manager import DatabaseManager

# Import Blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.vendor import vendor_bp
from routes.admin import admin_bp
from routes.api import api_bp

def format_indian_rupee(amount):
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return f"₹{amount}"
    
    if amount.is_integer():
        num = str(int(amount))
        dec_str = ""
    else:
        s = f"{amount:.2f}"
        parts = s.split('.')
        num = parts[0]
        dec_str = "." + parts[1]
        if dec_str == ".00":
            dec_str = ""
            
    if len(num) <= 3:
        int_part = num
    else:
        last_three = num[-3:]
        rest = num[:-3]
        groups = []
        while len(rest) > 2:
            groups.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.append(rest)
        groups.reverse()
        int_part = ",".join(groups) + "," + last_three
        
    return f"₹{int_part}{dec_str}"

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
        
    app.jinja_env.filters['rupee'] = format_indian_rupee
    return app

def _seed_default_admin(db_mgr):
    """Creates a default admin user, 8 vendors, 1 pending vendor, 12 categories, 96 products and runs the Pillow image generator."""
    try:
        from utils.helpers import hash_password
        from utils.seed_data import CATEGORIES, VENDORS, PRODUCTS, generate_seed_image
        
        # 1. Seed admin
        admin_exists = db_mgr.execute_query("SELECT id FROM users WHERE role = 'admin'")
        if not admin_exists:
            admin_pw_hash = hash_password('admin123')
            db_mgr.execute_non_query(
                "INSERT INTO users (username, email, password_hash, role, status) "
                "VALUES ('admin', 'admin@nexusmarket.com', %s, 'admin', 'active')",
                [admin_pw_hash]
            )
            print("[DATABASE SEED] Default admin account seeded: admin@nexusmarket.com / admin123")
            
        # 2. Seed categories (ensure all 12 are in db)
        for cat in CATEGORIES:
            cat_exists = db_mgr.execute_query("SELECT id FROM categories WHERE slug = %s", [cat['slug']])
            if not cat_exists:
                db_mgr.execute_non_query(
                    "INSERT INTO categories (name, description, slug) VALUES (%s, %s, %s)",
                    [cat['name'], cat['description'], cat['slug']]
                )
        print("[DATABASE SEED] Categories verified/seeded.")
        
        # 3. Seed 8 approved vendors
        for v in VENDORS:
            v_exists = db_mgr.execute_query("SELECT id FROM users WHERE email = %s", [v['email']])
            if not v_exists:
                pw_hash = hash_password('vendor123')
                v_user_id = db_mgr.execute_non_query(
                    "INSERT INTO users (username, email, password_hash, role, status) "
                    "VALUES (%s, %s, %s, 'vendor', 'active')",
                    [v['username'], v['email'], pw_hash]
                )
                db_mgr.execute_non_query(
                    "INSERT INTO vendors (user_id, business_name, description, status, rating) "
                    "VALUES (%s, %s, %s, 'approved', 4.5)",
                    [v_user_id, v['business_name'], v['description']]
                )
                
        # Seed 1 pending vendor for dashboard approval checks
        pending_exists = db_mgr.execute_query("SELECT id FROM users WHERE email = 'urban@trends.com'")
        if not pending_exists:
            pw_hash = hash_password('vendor123')
            pv_user_id = db_mgr.execute_non_query(
                "INSERT INTO users (username, email, password_hash, role, status) "
                "VALUES ('urban_trends', 'urban@trends.com', %s, 'vendor', 'active')",
                [pw_hash]
            )
            db_mgr.execute_non_query(
                "INSERT INTO vendors (user_id, business_name, description, status, rating) "
                "VALUES (%s, 'Urban Trends', 'Modern streetwear and premium accessories.', 'pending', 0.0)",
                [pv_user_id]
            )
        print("[DATABASE SEED] Vendors verified/seeded.")
        
        # Build category & vendor ID lookups
        cat_rows = db_mgr.execute_query("SELECT id, name, slug FROM categories")
        cat_map = {row['name']: row['id'] for row in cat_rows}
        cat_slug_map = {row['name']: row['slug'] for row in cat_rows}
        
        v_rows = db_mgr.execute_query("SELECT id, business_name FROM vendors")
        vendor_map = {row['business_name']: row['id'] for row in v_rows}
        
        # 4. Seed products and generate card images
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for idx, p in enumerate(PRODUCTS):
            # Check if product exists
            prod_exists = db_mgr.execute_query("SELECT id FROM products WHERE name = %s", [p['name']])
            
            # Determine image filename and path
            if 'image_file' in p:
                img_filename = p['image_file']
            else:
                clean_name = re.sub(r'[^a-zA-Z0-9]', '_', p['name'].lower())
                img_filename = f"{clean_name}.jpg"
                
            img_rel_path = f"images/products/{img_filename}"
            img_abs_path = os.path.join(base_dir, 'static', 'images', 'products', img_filename)
            
            # Generate the image if it doesn't exist
            if not os.path.exists(img_abs_path):
                cat_slug = cat_slug_map.get(p['category'], 'general')
                try:
                    generate_seed_image(p['name'], cat_slug, img_abs_path)
                except Exception as img_err:
                    print(f"[IMAGE GENERATOR ERROR] Failed to generate {img_filename}: {img_err}")
            
            if not prod_exists:
                cat_id = cat_map.get(p['category'])
                vendor_id = vendor_map.get(p['vendor'])
                if cat_id and vendor_id:
                    # Make every 10th product featured (approx 10 featured items)
                    is_featured = 1 if idx % 10 == 0 else 0
                    db_mgr.execute_non_query(
                        "INSERT INTO products (vendor_id, category_id, name, description, price, stock, image_url, status, average_rating, is_featured, discount_percentage) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', %s, %s, %s)",
                        [vendor_id, cat_id, p['name'], p['description'], p['price'], p['stock'], img_rel_path, p['rating'], is_featured, p.get('discount', 0)]
                    )
        print("[DATABASE SEED] 96+ product catalog successfully verified and seeded.")
    except Exception as e:
        print(f"[DATABASE SEED ERROR] Failed to seed default data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
