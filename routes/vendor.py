from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db_manager import DatabaseManager
from services.ai_service import AIService
from routes.auth import vendor_required
from utils.helpers import save_uploaded_file

vendor_bp = Blueprint('vendor', __name__)
db = DatabaseManager()

def _get_vendor_id():
    """Helper to fetch vendor database primary key from user_id."""
    user_id = session['user_id']
    vendor_rows = db.execute_query("SELECT id FROM vendors WHERE user_id = %s", [user_id])
    return vendor_rows[0]['id'] if vendor_rows else None

# ==========================================
# 1. Vendor Dashboard & Forecasts
# ==========================================
@vendor_bp.route('/vendor/dashboard')
@vendor_required
def dashboard():
    vendor_id = _get_vendor_id()
    if not vendor_id:
        flash('Vendor registration details missing.', 'danger')
        return redirect(url_for('user.index'))
        
    # Stats Overview
    stats = db.execute_query(
        "SELECT "
        "  COALESCE(SUM(oi.price * oi.quantity), 0) as total_earnings, "
        "  COALESCE(SUM(oi.quantity), 0) as items_sold, "
        "  COUNT(DISTINCT oi.order_id) as total_orders "
        "FROM order_items oi "
        "JOIN orders o ON oi.order_id = o.id "
        "WHERE oi.vendor_id = %s AND o.payment_status = 'paid'", [vendor_id]
    )[0]
    
    # AI Inventory warning counts
    inv_analysis = AIService.analyze_inventory(vendor_id)
    low_stock_count = len(inv_analysis['alerts'])
    
    # Recent Vendor Orders
    recent_orders = db.execute_query(
        "SELECT o.id, o.created_at, o.status, SUM(oi.price * oi.quantity) as order_val "
        "FROM order_items oi "
        "JOIN orders o ON oi.order_id = o.id "
        "WHERE oi.vendor_id = %s "
        "GROUP BY o.id ORDER BY o.created_at DESC LIMIT 5", [vendor_id]
    )
    
    # AI Predictive Sales Analytics
    forecast = AIService.get_sales_forecast(vendor_id, days=30)
    
    return render_template('vendor/dashboard.html', 
                           stats=stats, 
                           low_stock_count=low_stock_count, 
                           recent_orders=recent_orders,
                           forecast=forecast)


# ==========================================
# 2. Product Management (CRUD)
# ==========================================
@vendor_bp.route('/vendor/products')
@vendor_required
def products():
    vendor_id = _get_vendor_id()
    
    products_list = db.execute_query(
        "SELECT p.*, c.name as category_name "
        "FROM products p "
        "JOIN categories c ON p.category_id = c.id "
        "WHERE p.vendor_id = %s ORDER BY p.created_at DESC", [vendor_id]
    )
    return render_template('vendor/products.html', products=products_list)


@vendor_bp.route('/vendor/products/add', methods=['GET', 'POST'])
@vendor_required
def product_add():
    vendor_id = _get_vendor_id()
    categories = db.execute_query("SELECT * FROM categories")
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        description = request.form.get('description', '').strip()
        
        # Image upload
        file = request.files.get('product_image')
        image_url = 'default_product.png'
        
        if not name or not category_id or price is None or stock is None:
            flash('Please complete all required entries.', 'danger')
            return render_template('vendor/product_form.html', categories=categories, action='Add')
            
        if file and file.filename != '':
            saved_path = save_uploaded_file(file, 'products')
            if saved_path:
                image_url = saved_path
            else:
                flash('Invalid image format. Allowed: JPG, PNG, GIF.', 'danger')
                return render_template('vendor/product_form.html', categories=categories, action='Add')
                
        try:
            db.execute_non_query(
                "INSERT INTO products (vendor_id, category_id, name, description, price, stock, image_url, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')",
                [vendor_id, category_id, name, description, price, stock, image_url]
            )
            flash('Product created successfully!', 'success')
            return redirect(url_for('vendor.products'))
        except Exception as e:
            flash('Could not create product.', 'danger')
            print(f"[PRODUCT ADD ERROR] {e}")
            
    return render_template('vendor/product_form.html', categories=categories, action='Add', product=None)


@vendor_bp.route('/vendor/products/edit/<int:product_id>', methods=['GET', 'POST'])
@vendor_required
def product_edit(product_id):
    vendor_id = _get_vendor_id()
    categories = db.execute_query("SELECT * FROM categories")
    
    # Verify product ownership
    product_rows = db.execute_query(
        "SELECT * FROM products WHERE id = %s AND vendor_id = %s", [product_id, vendor_id]
    )
    if not product_rows:
        flash('Product not found or unauthorized access.', 'danger')
        return redirect(url_for('vendor.products'))
        
    product = product_rows[0]
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'active')
        
        file = request.files.get('product_image')
        image_url = product['image_url']
        
        if not name or not category_id or price is None or stock is None:
            flash('Please complete all required fields.', 'danger')
            return render_template('vendor/product_form.html', categories=categories, action='Edit', product=product)
            
        if file and file.filename != '':
            saved_path = save_uploaded_file(file, 'products')
            if saved_path:
                image_url = saved_path
            else:
                flash('Invalid image format.', 'danger')
                return render_template('vendor/product_form.html', categories=categories, action='Edit', product=product)
                
        try:
            db.execute_non_query(
                "UPDATE products "
                "SET category_id = %s, name = %s, description = %s, price = %s, stock = %s, image_url = %s, status = %s "
                "WHERE id = %s AND vendor_id = %s",
                [category_id, name, description, price, stock, image_url, status, product_id, vendor_id]
            )
            flash('Product updated successfully!', 'success')
            return redirect(url_for('vendor.products'))
        except Exception as e:
            flash('Could not update product.', 'danger')
            print(f"[PRODUCT EDIT ERROR] {e}")
            
    return render_template('vendor/product_form.html', categories=categories, action='Edit', product=product)


@vendor_bp.route('/vendor/products/delete/<int:product_id>', methods=['POST'])
@vendor_required
def product_delete(product_id):
    vendor_id = _get_vendor_id()
    
    # Verify product ownership
    product_rows = db.execute_query(
        "SELECT id FROM products WHERE id = %s AND vendor_id = %s", [product_id, vendor_id]
    )
    if not product_rows:
        flash('Product not found or unauthorized access.', 'danger')
        return redirect(url_for('vendor.products'))
        
    try:
        # Check if product is in any orders
        order_check = db.execute_query(
            "SELECT COUNT(*) as order_count FROM order_items WHERE product_id = %s", [product_id]
        )
        if order_check and order_check[0]['order_count'] > 0:
            # Instead of deleting, mark inactive to preserve referential integrity of invoices
            db.execute_non_query("UPDATE products SET status = 'inactive' WHERE id = %s", [product_id])
            flash('Product has order history. It has been deactivated instead of deleted.', 'warning')
        else:
            db.execute_non_query("DELETE FROM products WHERE id = %s", [product_id])
            flash('Product deleted successfully.', 'success')
    except Exception as e:
        flash('Could not delete product.', 'danger')
        print(f"[PRODUCT DELETE ERROR] {e}")
        
    return redirect(url_for('vendor.products'))


# ==========================================
# 3. Order Management for Vendors
# ==========================================
@vendor_bp.route('/vendor/orders')
@vendor_required
def orders():
    vendor_id = _get_vendor_id()
    
    # Get all order items belonging to this vendor
    order_items = db.execute_query(
        "SELECT oi.*, p.name as product_name, o.created_at, o.status as order_status, o.shipping_address "
        "FROM order_items oi "
        "JOIN orders o ON oi.order_id = o.id "
        "JOIN products p ON oi.product_id = p.id "
        "WHERE oi.vendor_id = %s "
        "ORDER BY o.created_at DESC", [vendor_id]
    )
    
    return render_template('vendor/orders.html', order_items=order_items)


@vendor_bp.route('/vendor/orders/update/<int:order_id>', methods=['POST'])
@vendor_required
def order_update_status(order_id):
    vendor_id = _get_vendor_id()
    new_status = request.form.get('status')
    
    # Confirm vendor owns at least one item in the order
    order_check = db.execute_query(
        "SELECT COUNT(*) as item_count FROM order_items WHERE order_id = %s AND vendor_id = %s",
        [order_id, vendor_id]
    )
    if not order_check or order_check[0]['item_count'] == 0:
        flash('Unauthorized access to order.', 'danger')
        return redirect(url_for('vendor.orders'))
        
    try:
        # Update order status site-wide (in a fully decentralized model, status could be per-item,
        # but here we update the main order status for user-friendly simplicity)
        db.execute_non_query(
            "UPDATE orders SET status = %s WHERE id = %s", [new_status, order_id]
        )
        flash(f"Order #{order_id} status updated to '{new_status}'.", 'success')
    except Exception as e:
        flash('Could not update status.', 'danger')
        print(f"[ORDER STATUS UPDATE ERROR] {e}")
        
    return redirect(url_for('vendor.orders'))


# ==========================================
# 4. Sales and Inventory Predictions
# ==========================================
@vendor_bp.route('/vendor/analytics')
@vendor_required
def analytics():
    vendor_id = _get_vendor_id()
    
    # AI Inventory Analyzer
    inventory_analysis = AIService.analyze_inventory(vendor_id)
    
    # AI Sales Reports
    performance = AIService.get_sales_performance_report(vendor_id)
    
    # Forecast Details
    forecast = AIService.get_sales_forecast(vendor_id)
    
    return render_template('vendor/analytics.html',
                           report=inventory_analysis['report'],
                           alerts=inventory_analysis['alerts'],
                           suggestions=inventory_analysis['restock_suggestions'],
                           top_selling=performance['top_selling'],
                           dead_inventory=performance['dead_inventory'],
                           forecast=forecast)
