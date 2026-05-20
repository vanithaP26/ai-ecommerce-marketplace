from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.db_manager import DatabaseManager
from services.ai_service import AIService
from routes.auth import login_required, customer_required
from utils.helpers import generate_invoice_html
import os

user_bp = Blueprint('user', __name__)
db = DatabaseManager()

# ==========================================
# 1. Homepage & Recommendations
# ==========================================
@user_bp.route('/')
def index():
    user_id = session.get('user_id')
    
    # 1. Fetch Categories (cached for speed optimization)
    categories = db.execute_query("SELECT * FROM categories", cache=True)
    
    # 2. Fetch AI Personalized Recommendations
    recommendations = AIService.get_recommendations(user_id=user_id, limit=6)
    
    # 3. Fetch Trending Products (highest sales)
    trending_products = db.execute_query(
        "SELECT p.*, v.business_name, COUNT(oi.id) as sales_count "
        "FROM products p "
        "JOIN vendors v ON p.vendor_id = v.id "
        "LEFT JOIN order_items oi ON p.id = oi.product_id "
        "WHERE p.status = 'active' AND v.status = 'approved' "
        "GROUP BY p.id "
        "ORDER BY sales_count DESC, p.average_rating DESC "
        "LIMIT 6", cache=True
    )
    
    return render_template('user/home.html', 
                           categories=categories, 
                           recommendations=recommendations, 
                           trending=trending_products)


# ==========================================
# 2. Product Browsing & Pagination
# ==========================================
@user_bp.route('/products')
def browse():
    category_id = request.args.get('category')
    sort_by = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page
    
    # Building query dynamically
    query_str = (
        "SELECT p.*, v.business_name, c.name as category_name "
        "FROM products p "
        "JOIN vendors v ON p.vendor_id = v.id "
        "JOIN categories c ON p.category_id = c.id "
        "WHERE p.status = 'active' AND v.status = 'approved'"
    )
    params = []
    
    if category_id:
        query_str += " AND p.category_id = %s"
        params.append(category_id)
        
    if min_price is not None:
        query_str += " AND p.price >= %s"
        params.append(min_price)
        
    if max_price is not None:
        query_str += " AND p.price <= %s"
        params.append(max_price)
        
    # Total Count Query for Pagination
    count_query = f"SELECT COUNT(*) as total_count FROM ({query_str}) as sub"
    total_records = db.execute_query(count_query, params)
    total_count = total_records[0]['total_count'] if total_records else 0
    total_pages = (total_count + per_page - 1) // per_page
    
    # Order By
    if sort_by == 'price_low':
        query_str += " ORDER BY p.price ASC"
    elif sort_by == 'price_high':
        query_str += " ORDER BY p.price DESC"
    elif sort_by == 'rating':
        query_str += " ORDER BY p.average_rating DESC"
    else:
        query_str += " ORDER BY p.created_at DESC"
        
    # Limit and Offset
    query_str += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    products = db.execute_query(query_str, params)
    categories = db.execute_query("SELECT * FROM categories", cache=True)
    
    return render_template('user/browse.html', 
                           products=products, 
                           categories=categories, 
                           current_category=category_id,
                           sort=sort_by,
                           min_price=min_price,
                           max_price=max_price,
                           page=page,
                           total_pages=total_pages)


# ==========================================
# 3. Intelligent Search
# ==========================================
@user_bp.route('/search')
def search():
    original_query = request.args.get('q', '').strip()
    corrected_query = ""
    
    if not original_query:
        return redirect(url_for('user.browse'))
        
    # Fetch base products
    like_q = f"%{original_query}%"
    products = db.execute_query(
        "SELECT p.*, v.business_name, c.name as category_name "
        "FROM products p "
        "JOIN vendors v ON p.vendor_id = v.id "
        "JOIN categories c ON p.category_id = c.id "
        "WHERE (p.name LIKE %s OR p.description LIKE %s OR c.name LIKE %s) "
        "AND p.status = 'active' AND v.status = 'approved'",
        [like_q, like_q, like_q]
    )
    
    # AI Typo Correction if no products found
    if not products:
        corrected_query = AIService.typo_correction(original_query)
        if corrected_query != original_query:
            like_cq = f"%{corrected_query}%"
            products = db.execute_query(
                "SELECT p.*, v.business_name, c.name as category_name "
                "FROM products p "
                "JOIN vendors v ON p.vendor_id = v.id "
                "JOIN categories c ON p.category_id = c.id "
                "WHERE (p.name LIKE %s OR p.description LIKE %s OR c.name LIKE %s) "
                "AND p.status = 'active' AND v.status = 'approved'",
                [like_cq, like_cq, like_cq]
            )
            
    # AI Search Ranking Optimization
    query_to_rank = corrected_query if (corrected_query and products) else original_query
    products = AIService.search_ranking(products, query_to_rank)
    
    # Log search queries for behavior tracking
    user_id = session.get('user_id')
    AIService.log_action(user_id, None, 'search', f"Query: {original_query} | Corrected: {corrected_query}")
    
    categories = db.execute_query("SELECT * FROM categories", cache=True)
    
    return render_template('user/search_results.html', 
                           products=products, 
                           query=original_query, 
                           corrected_query=corrected_query,
                           categories=categories)


# ==========================================
# 4. Product Detail & Similar Items
# ==========================================
@user_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    user_id = session.get('user_id')
    
    # Load primary product
    product_rows = db.execute_query(
        "SELECT p.*, v.business_name, v.id as vendor_db_id, c.name as category_name "
        "FROM products p "
        "JOIN vendors v ON p.vendor_id = v.id "
        "JOIN categories c ON p.category_id = c.id "
        "WHERE p.id = %s", [product_id]
    )
    
    if not product_rows:
        flash('Product not found.', 'danger')
        return redirect(url_for('user.index'))
        
    product = product_rows[0]
    
    # Log product page view for personalized recommendation engines
    AIService.log_action(user_id, product_id, 'view')
    
    # Fetch Reviews
    reviews = db.execute_query(
        "SELECT r.*, u.username FROM reviews r "
        "JOIN users u ON r.user_id = u.id "
        "WHERE r.product_id = %s ORDER BY r.created_at DESC", [product_id]
    )
    
    # Fetch Similar Products (AI recommendations fallback / logic)
    similar_products = db.execute_query(
        "SELECT p.*, v.business_name FROM products p "
        "JOIN vendors v ON p.vendor_id = v.id "
        "WHERE p.category_id = %s AND p.id != %s AND p.status = 'active' AND v.status = 'approved' "
        "ORDER BY p.average_rating DESC LIMIT 4", [product['category_id'], product_id]
    )
    
    # Verify if user has bought this item (enables review submission)
    can_review = False
    if user_id and session.get('role') == 'customer':
        orders_check = db.execute_query(
            "SELECT COUNT(oi.id) as bought_count "
            "FROM order_items oi "
            "JOIN orders o ON oi.order_id = o.id "
            "WHERE o.user_id = %s AND oi.product_id = %s AND o.payment_status = 'paid'",
            [user_id, product_id]
        )
        if orders_check and orders_check[0]['bought_count'] > 0:
            # Check if user already reviewed
            already_reviewed = db.execute_query(
                "SELECT id FROM reviews WHERE user_id = %s AND product_id = %s", [user_id, product_id]
            )
            if not already_reviewed:
                can_review = True
                
    # Review POST handling
    if request.method == 'POST' and can_review:
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            flash('Please specify a rating (1-5 stars).', 'danger')
        else:
            try:
                db.execute_non_query(
                    "INSERT INTO reviews (user_id, product_id, rating, comment) "
                    "VALUES (%s, %s, %s, %s)",
                    [user_id, product_id, rating, comment]
                )
                
                # Update product average rating
                avg_rows = db.execute_query(
                    "SELECT AVG(rating) as avg_rating FROM reviews WHERE product_id = %s", [product_id]
                )
                new_avg = avg_rows[0]['avg_rating'] if avg_rows else rating
                
                db.execute_non_query(
                    "UPDATE products SET average_rating = %s WHERE id = %s", [new_avg, product_id]
                )
                
                flash('Review submitted successfully!', 'success')
                return redirect(url_for('user.product_detail', product_id=product_id))
            except Exception as e:
                flash('Could not add review.', 'danger')
                print(f"[REVIEW SAVE ERROR] {e}")
                
    return render_template('user/product_detail.html', 
                           product=product, 
                           reviews=reviews, 
                           similar=similar_products, 
                           can_review=can_review)


# ==========================================
# 5. Shopping Cart
# ==========================================
@user_bp.route('/cart')
@customer_required
def cart():
    user_id = session['user_id']
    cart_items = db.execute_query(
        "SELECT c.id as cart_id, c.quantity, p.*, v.business_name "
        "FROM cart c "
        "JOIN products p ON c.product_id = p.id "
        "JOIN vendors v ON p.vendor_id = v.id "
        "WHERE c.user_id = %s", [user_id]
    )
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('user/cart.html', cart_items=cart_items, total=total)


@user_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@customer_required
def cart_add(product_id):
    user_id = session['user_id']
    qty = request.form.get('quantity', 1, type=int)
    
    # Verify stock
    product_rows = db.execute_query("SELECT stock, name FROM products WHERE id = %s", [product_id])
    if not product_rows:
        flash('Product not found.', 'danger')
        return redirect(url_for('user.index'))
        
    product = product_rows[0]
    if product['stock'] < qty:
        flash(f"Insufficient stock for {product['name']}. Available: {product['stock']}", 'danger')
        return redirect(url_for('user.product_detail', product_id=product_id))
        
    # Check if item exists in cart
    exists = db.execute_query("SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s", [user_id, product_id])
    
    try:
        if exists:
            new_qty = exists[0]['quantity'] + qty
            if product['stock'] < new_qty:
                flash(f"Cart limit exceeded. Total requested: {new_qty} exceeds stock: {product['stock']}", 'danger')
            else:
                db.execute_non_query(
                    "UPDATE cart SET quantity = %s WHERE id = %s", [new_qty, exists[0]['id']]
                )
                flash('Cart updated successfully.', 'success')
        else:
            db.execute_non_query(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                [user_id, product_id, qty]
            )
            flash('Product added to cart.', 'success')
            
        # Log action for recommendation optimization
        AIService.log_action(user_id, product_id, 'cart_add')
    except Exception as e:
        flash('Could not update cart.', 'danger')
        print(f"[CART ADD ERROR] {e}")
        
    return redirect(url_for('user.cart'))


@user_bp.route('/cart/update/<int:cart_id>', methods=['POST'])
@customer_required
def cart_update(cart_id):
    user_id = session['user_id']
    qty = request.form.get('quantity', type=int)
    
    if not qty or qty < 1:
        return redirect(url_for('user.cart'))
        
    # Verify cart ownership
    cart_rows = db.execute_query(
        "SELECT c.*, p.stock, p.name FROM cart c JOIN products p ON c.product_id = p.id WHERE c.id = %s AND c.user_id = %s",
        [cart_id, user_id]
    )
    if not cart_rows:
        flash('Cart entry not found.', 'danger')
        return redirect(url_for('user.cart'))
        
    item = cart_rows[0]
    if item['stock'] < qty:
        flash(f"Insufficient stock for {item['name']}. Available: {item['stock']}", 'danger')
    else:
        db.execute_non_query("UPDATE cart SET quantity = %s WHERE id = %s", [qty, cart_id])
        flash('Cart quantity updated.', 'success')
        
    return redirect(url_for('user.cart'))


@user_bp.route('/cart/delete/<int:cart_id>')
@customer_required
def cart_delete(cart_id):
    user_id = session['user_id']
    db.execute_non_query("DELETE FROM cart WHERE id = %s AND user_id = %s", [cart_id, user_id])
    flash('Item removed from cart.', 'success')
    return redirect(url_for('user.cart'))


# ==========================================
# 6. Wishlist Management
# ==========================================
@user_bp.route('/wishlist')
@customer_required
def wishlist():
    user_id = session['user_id']
    wishlist_items = db.execute_query(
        "SELECT w.id as wishlist_id, p.*, v.business_name "
        "FROM wishlist w "
        "JOIN products p ON w.product_id = p.id "
        "JOIN vendors v ON p.vendor_id = v.id "
        "WHERE w.user_id = %s", [user_id]
    )
    return render_template('user/wishlist.html', wishlist_items=wishlist_items)


@user_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@customer_required
def wishlist_toggle(product_id):
    user_id = session['user_id']
    
    exists = db.execute_query(
        "SELECT id FROM wishlist WHERE user_id = %s AND product_id = %s", [user_id, product_id]
    )
    
    try:
        if exists:
            db.execute_non_query("DELETE FROM wishlist WHERE id = %s", [exists[0]['id']])
            flash('Removed from wishlist.', 'success')
        else:
            db.execute_non_query("INSERT INTO wishlist (user_id, product_id) VALUES (%s, %s)", [user_id, product_id])
            flash('Added to wishlist.', 'success')
    except Exception as e:
        flash('Could not toggle wishlist.', 'danger')
        print(f"[WISHLIST ERROR] {e}")
        
    return redirect(request.referrer or url_for('user.wishlist'))


# ==========================================
# 7. Checkout & Fraud Auditing
# ==========================================
@user_bp.route('/checkout', methods=['GET', 'POST'])
@customer_required
def checkout():
    user_id = session['user_id']
    
    # Load cart items
    cart_items = db.execute_query(
        "SELECT c.quantity, p.* FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id = %s", [user_id]
    )
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('user.cart'))
        
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address', '').strip()
        payment_method = request.form.get('payment_method', 'Credit Card')
        
        if not shipping_address:
            flash('Please enter a shipping address.', 'danger')
            return render_template('user/checkout.html', cart_items=cart_items, total=total)
            
        # Inventory verification right before finalizing order (concurrency check)
        for item in cart_items:
            live_stock = db.execute_query("SELECT stock, name FROM products WHERE id = %s", [item['id']])[0]
            if live_stock['stock'] < item['quantity']:
                flash(f"Inventory shortfall! Product: '{live_stock['name']}' has only {live_stock['stock']} units left. Please adjust your cart.", 'danger')
                return redirect(url_for('user.cart'))
                
        # AI Fraud Detection
        is_fraud, fraud_reason = AIService.is_transaction_suspicious(user_id, shipping_address, total)
        
        try:
            # Set order status: If marked suspicious, hold it for review, else mark processing
            order_status = 'pending' if is_fraud else 'processing'
            payment_status = 'paid'  # Simplification for checkout simulation
            
            # 1. Create order record
            order_id = db.execute_non_query(
                "INSERT INTO orders (user_id, total_amount, status, payment_status, shipping_address, tracking_number) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                [user_id, total, order_status, payment_status, shipping_address, f"TRK-{uuid.uuid4().hex[:10].upper()}"]
            )
            
            # 2. Insert items and decrement stocks
            for item in cart_items:
                # Add order items
                db.execute_non_query(
                    "INSERT INTO order_items (order_id, product_id, price, quantity, vendor_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    [order_id, item['id'], item['price'], item['quantity'], item['vendor_id']]
                )
                # Decrement stock
                db.execute_non_query(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    [item['quantity'], item['id']]
                )
                
                # Log action to behavior tracker
                AIService.log_action(user_id, item['id'], 'purchase')
                
            # 3. Save mock transaction payment
            db.execute_non_query(
                "INSERT INTO payments (order_id, payment_method, transaction_id, amount, status) "
                "VALUES (%s, %s, %s, %s, 'completed')",
                [order_id, payment_method, f"TXN-{uuid.uuid4().hex[:12].upper()}", total]
            )
            
            # 4. Clear shopping cart
            db.execute_non_query("DELETE FROM cart WHERE user_id = %s", [user_id])
            
            # 5. Generate beautiful HTML invoice
            order_data = db.execute_query("SELECT * FROM orders WHERE id = %s", [order_id])[0]
            user_data = db.execute_query("SELECT id, username, email FROM users WHERE id = %s", [user_id])[0]
            items_detailed = db.execute_query(
                "SELECT oi.*, p.name as product_name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = %s",
                [order_id]
            )
            
            # Helper handles file output and writes to static/uploads/invoices
            invoice_rel_path = generate_invoice_html(order_data, user_data, items_detailed)
            
            # Save invoice path in order
            db.execute_non_query("UPDATE orders SET invoice_path = %s WHERE id = %s", [invoice_rel_path, order_id])
            
            # If transaction was flagged as fraud
            if is_fraud:
                db.execute_non_query(
                    "INSERT INTO analytics_logs (user_id, action_type, action_details) "
                    "VALUES (%s, 'fraud_flag', %s)",
                    [user_id, f"Order #{order_id} flagged: {fraud_reason}"]
                )
                flash('Your order has been placed. Due to random safety reviews, it is pending administrative authorization.', 'warning')
            else:
                flash('Order placed and paid successfully!', 'success')
                
            return redirect(url_for('user.order_details', order_id=order_id))
            
        except Exception as e:
            flash('Error finalizing order. Please check billing parameters.', 'danger')
            print(f"[CHECKOUT ERROR] {e}")
            
    return render_template('user/checkout.html', cart_items=cart_items, total=total)


# ==========================================
# 8. Order Tracking & Invoices
# ==========================================
@user_bp.route('/orders')
@login_required
def orders_history():
    user_id = session['user_id']
    role = session['role']
    
    if role == 'customer':
        orders = db.execute_query("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", [user_id])
    else:
        # Vendor/Admin should not list orders through this endpoint
        orders = []
        
    return render_template('user/orders_history.html', orders=orders)


@user_bp.route('/orders/<int:order_id>')
@login_required
def order_details(order_id):
    user_id = session['user_id']
    role = session['role']
    
    # Load order
    order_rows = db.execute_query("SELECT * FROM orders WHERE id = %s", [order_id])
    if not order_rows:
        flash('Order not found.', 'danger')
        return redirect(url_for('user.orders_history'))
        
    order = order_rows[0]
    
    # Verification: Access control
    if role == 'customer' and order['user_id'] != user_id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.orders_history'))
        
    # Get items
    items = db.execute_query(
        "SELECT oi.*, p.name as product_name, p.image_url "
        "FROM order_items oi "
        "JOIN products p ON oi.product_id = p.id "
        "WHERE oi.order_id = %s", [order_id]
    )
    
    # Vendor constraint: show only their items
    if role == 'vendor':
        vendor = db.execute_query("SELECT id FROM vendors WHERE user_id = %s", [user_id])[0]
        items = [i for i in items if i['vendor_id'] == vendor['id']]
        if not items:
            flash('Unauthorized.', 'danger')
            return redirect(url_for('vendor.dashboard'))
            
    return render_template('user/order_details.html', order=order, items=items)


# ==========================================
# 9. Profile Settings
# ==========================================
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validations
        if not username or not email:
            flash('All credentials are required.', 'danger')
            return redirect(url_for('user.profile'))
            
        try:
            # Check unique constraints ignoring self
            exists = db.execute_query(
                "SELECT id FROM users WHERE (username = %s OR email = %s) AND id != %s",
                [username, email, user_id]
            )
            if exists:
                flash('Username or Email already in use by another user.', 'danger')
            else:
                db.execute_non_query(
                    "UPDATE users SET username = %s, email = %s WHERE id = %s",
                    [username, email, user_id]
                )
                session['username'] = username
                session['email'] = email
                flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash('Failed to update details.', 'danger')
            print(f"[PROFILE UPDATE ERROR] {e}")
            
    user_data = db.execute_query("SELECT * FROM users WHERE id = %s", [user_id])[0]
    return render_template('user/profile.html', user=user_data)


# ==========================================
# 10. Product Comparison Matrix
# ==========================================
@user_bp.route('/compare')
def compare():
    # Load comparing items from session
    compare_ids = session.get('compare_list', [])
    products = []
    
    if compare_ids:
        # Load details
        ids_placeholders = ",".join(["%s"] * len(compare_ids))
        products = db.execute_query(
            f"SELECT p.*, v.business_name, c.name as category_name "
            f"FROM products p "
            f"JOIN vendors v ON p.vendor_id = v.id "
            f"JOIN categories c ON p.category_id = c.id "
            f"WHERE p.id IN ({ids_placeholders})", compare_ids
        )
        
    return render_template('user/compare.html', products=products)


@user_bp.route('/compare/add/<int:product_id>', methods=['POST'])
def compare_add(product_id):
    compare_ids = session.get('compare_list', [])
    
    if product_id in compare_ids:
        flash('Product is already in the comparison list.', 'info')
    elif len(compare_ids) >= 3:
        flash('You can compare a maximum of 3 products at a time.', 'warning')
    else:
        compare_ids.append(product_id)
        session['compare_list'] = compare_ids
        flash('Product added to comparison matrix.', 'success')
        
    return redirect(request.referrer or url_for('user.compare'))


@user_bp.route('/compare/remove/<int:product_id>')
def compare_remove(product_id):
    compare_ids = session.get('compare_list', [])
    if product_id in compare_ids:
        compare_ids.remove(product_id)
        session['compare_list'] = compare_ids
        flash('Product removed from comparison matrix.', 'success')
    return redirect(url_for('user.compare'))
