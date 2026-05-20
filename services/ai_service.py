import math
from models.db_manager import DatabaseManager

db = DatabaseManager()

class AIService:
    
    # ==========================================
    # A. Smart Product Recommendation System
    # ==========================================
    @staticmethod
    def get_recommendations(user_id=None, limit=6):
        """
        Retrieves recommended products for a user.
        If user_id is None or has no history, uses a 'cold start' strategy (popular and highly rated).
        Otherwise, scores products based on user views, purchase categories, and product ratings.
        """
        # Fetch all active products
        all_products = db.execute_query(
            "SELECT p.*, v.business_name, c.name as category_name "
            "FROM products p "
            "JOIN vendors v ON p.vendor_id = v.id "
            "JOIN categories c ON p.category_id = c.id "
            "WHERE p.status = 'active' AND v.status = 'approved'"
        )
        
        if not all_products:
            return []
            
        # Get purchase history count for all products to determine general popularity
        purchases = db.execute_query(
            "SELECT product_id, COUNT(*) as sales_count FROM order_items GROUP BY product_id"
        )
        sales_map = {p['product_id']: p['sales_count'] for p in purchases}
        
        # Cold start or guest user
        if not user_id:
            # Score = (sales * 0.5) + (rating * 2.0)
            scored = []
            for p in all_products:
                sales = sales_map.get(p['id'], 0)
                rating = float(p['average_rating'] or 0.0)
                score = (sales * 0.5) + (rating * 2.0)
                scored.append((p, score))
            scored.sort(key=lambda x: x[1], reverse=True)
            return [x[0] for x in scored[:limit]]
            
        # Personalized recommendations
        # 1. Fetch user's view logs (categories viewed)
        view_logs = db.execute_query(
            "SELECT p.category_id, COUNT(*) as view_count "
            "FROM analytics_logs a "
            "JOIN products p ON a.product_id = p.id "
            "WHERE a.user_id = %s AND a.action_type = 'view' "
            "GROUP BY p.category_id", [user_id]
        )
        viewed_categories = {log['category_id']: log['view_count'] for log in view_logs}
        
        # 2. Fetch user's purchased categories
        purchase_logs = db.execute_query(
            "SELECT p.category_id, COUNT(*) as buy_count "
            "FROM orders o "
            "JOIN order_items oi ON o.id = oi.order_id "
            "JOIN products p ON oi.product_id = p.id "
            "WHERE o.user_id = %s "
            "GROUP BY p.category_id", [user_id]
        )
        purchased_categories = {log['category_id']: log['buy_count'] for log in purchase_logs}
        
        # 3. Fetch products already in user's cart or wishlist (exclude or down-rank them)
        cart_wish_items = db.execute_query(
            "SELECT product_id FROM cart WHERE user_id = %s "
            "UNION SELECT product_id FROM wishlist WHERE user_id = %s", 
            [user_id, user_id]
        )
        exclude_ids = {item['product_id'] for item in cart_wish_items}
        
        # Score products
        scored_products = []
        for p in all_products:
            if p['id'] in exclude_ids:
                continue
                
            p_id = p['id']
            cat_id = p['category_id']
            rating = float(p['average_rating'] or 0.0)
            global_sales = sales_map.get(p_id, 0)
            
            # Base score from rating and global popularity
            score = (rating * 1.5) + (global_sales * 0.2)
            
            # Category interest boosts
            if cat_id in viewed_categories:
                score += viewed_categories[cat_id] * 2.0  # +2 points per view
                
            if cat_id in purchased_categories:
                score += purchased_categories[cat_id] * 5.0  # +5 points per purchase
                
            scored_products.append((p, score))
            
        # Sort and return
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in scored_products[:limit]]

    # ==========================================
    # B. Intelligent Search Optimization
    # ==========================================
    @staticmethod
    def levenshtein_distance(s1, s2):
        """Calculates Levenshtein distance between two strings (for typo correction)."""
        s1 = s1.lower()
        s2 = s2.lower()
        if len(s1) < len(s2):
            return AIService.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]

    @staticmethod
    def typo_correction(query):
        """Suggests typo-corrected keywords if no direct matches are found."""
        if not query or len(query) < 3:
            return query
            
        # Get all unique words from product names, categories and descriptions
        keywords = db.execute_query(
            "SELECT DISTINCT name FROM products WHERE status = 'active' "
            "UNION SELECT DISTINCT name FROM categories"
        )
        
        words = []
        for kw in keywords:
            words.extend(re.findall(r'\w+', kw['name'].lower()))
        words = list(set(words))
        
        query_words = query.lower().split()
        corrected_words = []
        
        for qw in query_words:
            if qw in words or len(qw) < 3:
                corrected_words.append(qw)
                continue
                
            # Find best match
            best_match = qw
            min_dist = 3  # Maximum threshold for typos
            
            for w in words:
                if abs(len(w) - len(qw)) > 2:
                    continue
                dist = AIService.levenshtein_distance(qw, w)
                if dist < min_dist:
                    min_dist = dist
                    best_match = w
            
            corrected_words.append(best_match)
            
        return " ".join(corrected_words)

    @staticmethod
    def search_ranking(products, query):
        """Ranks search results by matching quality across title, category, and description."""
        if not query:
            return products
            
        ranked_list = []
        query_terms = query.lower().split()
        
        for p in products:
            score = 0
            name_lower = p['name'].lower()
            desc_lower = (p['description'] or '').lower()
            cat_lower = (p.get('category_name') or '').lower()
            
            # 1. Whole phrase matches
            if query.lower() in name_lower:
                score += 15
            if query.lower() in cat_lower:
                score += 8
            
            # 2. Term matches
            for term in query_terms:
                if len(term) < 2:
                    continue
                if term in name_lower:
                    score += 5
                if term in cat_lower:
                    score += 3
                if term in desc_lower:
                    score += 1
                    
            # 3. Add rating boost
            score += float(p.get('average_rating') or 0.0) * 0.5
            
            ranked_list.append((p, score))
            
        ranked_list.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in ranked_list]

    @staticmethod
    def get_search_suggestions(prefix, limit=5):
        """Provides auto-suggestions based on keyword search index and past popular search queries."""
        if not prefix or len(prefix) < 2:
            return []
            
        # Get matches from product titles and categories
        like_query = f"{prefix}%"
        suggestions = db.execute_query(
            "SELECT DISTINCT name FROM products WHERE name LIKE %s AND status = 'active' "
            "UNION "
            "SELECT name FROM categories WHERE name LIKE %s "
            "LIMIT %s", [like_query, like_query, limit]
        )
        return [s['name'] for s in suggestions]

    # ==========================================
    # C. AI Sales Analytics
    # ==========================================
    @staticmethod
    def get_sales_forecast(vendor_id=None, days=30):
        """
        Uses Linear Regression (Least Squares) to forecast sales volume and revenue.
        If vendor_id is None, forecasts site-wide sales.
        """
        # Fetch actual sales grouped by date for the last 30 days
        params = []
        query = (
            "SELECT DATE(o.created_at) as date, SUM(oi.price * oi.quantity) as revenue, SUM(oi.quantity) as volume "
            "FROM orders o "
            "JOIN order_items oi ON o.id = oi.order_id "
            "WHERE o.payment_status = 'paid' "
        )
        if vendor_id:
            query += "AND oi.vendor_id = %s "
            params.append(vendor_id)
            
        query += "GROUP BY DATE(o.created_at) ORDER BY date ASC"
        sales_history = db.execute_query(query, params)
        
        # Prepare lists for X (time index 0..N-1) and Y (revenue/volume)
        n = len(sales_history)
        if n < 3:
            # Not enough data points to do a regression, return flat projection
            avg_rev = sum(s['revenue'] for s in sales_history) / max(n, 1) if n > 0 else 0
            avg_vol = sum(s['volume'] for s in sales_history) / max(n, 1) if n > 0 else 0
            return {
                'slope_revenue': 0.0,
                'predicted_revenue_next_period': float(avg_rev * days),
                'predicted_volume_next_period': int(avg_vol * days),
                'trend': 'stable',
                'history': sales_history
            }
            
        x = list(range(n))
        y_rev = [float(s['revenue']) for s in sales_history]
        y_vol = [int(s['volume']) for s in sales_history]
        
        # Linear Regression formulas: y = mx + c
        # m = (N*sum(xy) - sum(x)*sum(y)) / (N*sum(x^2) - (sum(x))^2)
        # c = (sum(y) - m*sum(x)) / N
        
        def calculate_slope_intercept(x_vals, y_vals):
            num_points = len(x_vals)
            sum_x = sum(x_vals)
            sum_y = sum(y_vals)
            sum_xx = sum(xv * xv for xv in x_vals)
            sum_xy = sum(xv * yv for xv, yv in zip(x_vals, y_vals))
            
            denominator = (num_points * sum_xx - sum_x * sum_x)
            if denominator == 0:
                return 0.0, sum_y / num_points
                
            m = (num_points * sum_xy - sum_x * sum_y) / denominator
            c = (sum_y - m * sum_x) / num_points
            return m, c
            
        m_rev, c_rev = calculate_slope_intercept(x, y_rev)
        m_vol, c_vol = calculate_slope_intercept(x, y_vol)
        
        # Project values for next periods (N to N + days - 1)
        predicted_revenue = 0.0
        predicted_volume = 0.0
        for i in range(n, n + days):
            projected_day_rev = max(m_rev * i + c_rev, 0.0)  # Avoid negative values
            projected_day_vol = max(m_vol * i + c_vol, 0.0)
            predicted_revenue += projected_day_rev
            predicted_volume += projected_day_vol
            
        trend = 'stable'
        if m_rev > 0.5:
            trend = 'upward'
        elif m_rev < -0.5:
            trend = 'downward'
            
        return {
            'slope_revenue': float(m_rev),
            'predicted_revenue_next_period': float(predicted_revenue),
            'predicted_volume_next_period': int(predicted_volume),
            'trend': trend,
            'history': sales_history
        }

    @staticmethod
    def get_sales_performance_report(vendor_id=None):
        """Identifies top-selling products and low-performing (dead) inventory."""
        params = []
        top_query = (
            "SELECT p.id, p.name, p.price, p.stock, SUM(oi.quantity) as units_sold, SUM(oi.price * oi.quantity) as sales_revenue "
            "FROM order_items oi "
            "JOIN products p ON oi.product_id = p.id "
            "JOIN orders o ON oi.order_id = o.id "
            "WHERE o.payment_status = 'paid' "
        )
        if vendor_id:
            top_query += "AND oi.vendor_id = %s "
            params.append(vendor_id)
            
        top_query += "GROUP BY p.id ORDER BY units_sold DESC LIMIT 5"
        top_selling = db.execute_query(top_query, params)
        
        # Dead inventory: Products with zero sales in last 30 days
        dead_query = (
            "SELECT p.id, p.name, p.price, p.stock, p.created_at "
            "FROM products p "
            "WHERE p.status = 'active' "
        )
        if vendor_id:
            dead_query += "AND p.vendor_id = %s "
        
        dead_query += (
            "AND p.id NOT IN ("
            "  SELECT DISTINCT oi.product_id "
            "  FROM order_items oi "
            "  JOIN orders o ON oi.order_id = o.id "
            "  WHERE o.payment_status = 'paid' AND o.created_at >= datetime('now', '-30 days')" if db.db_type == 'sqlite' else
            "  WHERE o.payment_status = 'paid' AND o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            ")"
        )
        
        dead_inventory = db.execute_query(dead_query, [vendor_id] if vendor_id else [])
        
        return {
            'top_selling': top_selling,
            'dead_inventory': dead_inventory
        }

    # ==========================================
    # D. Intelligent Inventory Optimization
    # ==========================================
    @staticmethod
    def analyze_inventory(vendor_id):
        """
        Analyzes inventory levels. Detects items near running out based on average daily velocity.
        Suggests restock metrics.
        """
        # Fetch vendor products
        products = db.execute_query(
            "SELECT id, name, stock, price FROM products WHERE vendor_id = %s AND status = 'active'",
            [vendor_id]
        )
        
        # Fetch sales velocity for the last 30 days
        # Daily sales velocity = (units sold in 30 days) / 30
        velocity_query = (
            "SELECT oi.product_id, SUM(oi.quantity) as total_qty "
            "FROM order_items oi "
            "JOIN orders o ON oi.order_id = o.id "
            "WHERE oi.vendor_id = %s AND o.payment_status = 'paid' "
        )
        if db.db_type == 'sqlite':
            velocity_query += "AND o.created_at >= datetime('now', '-30 days') "
        else:
            velocity_query += "AND o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) "
        velocity_query += "GROUP BY oi.product_id"
        
        velocity_data = db.execute_query(velocity_query, [vendor_id])
        velocity_map = {v['product_id']: (v['total_qty'] / 30.0) for v in velocity_data}
        
        inventory_report = []
        shortage_alerts = []
        restock_suggestions = []
        
        for p in products:
            p_id = p['id']
            daily_velocity = velocity_map.get(p_id, 0.0)
            stock = p['stock']
            
            # Days of stock remaining = stock / daily_velocity
            days_remaining = stock / daily_velocity if daily_velocity > 0 else 999
            
            status = 'healthy'
            if stock == 0:
                status = 'out_of_stock'
                shortage_alerts.append(p)
            elif days_remaining <= 7 or stock < 5:  # Low stock if less than 7 days of supply or < 5 items
                status = 'low_stock'
                shortage_alerts.append(p)
                
            # If stock is low or out, suggest restock quantity: 30 days of sales + safety margin (5 items)
            if status in ['out_of_stock', 'low_stock']:
                suggested_qty = math.ceil((daily_velocity * 30.0) - stock + 5)
                # Keep restock suggestions sensible (at least 10 items)
                suggested_qty = max(suggested_qty, 10)
                restock_suggestions.append({
                    'product_id': p_id,
                    'name': p['name'],
                    'current_stock': stock,
                    'daily_sales_velocity': round(daily_velocity, 2),
                    'suggested_restock': suggested_qty
                })
                
            inventory_report.append({
                'product_id': p_id,
                'name': p['name'],
                'stock': stock,
                'velocity': round(daily_velocity, 2),
                'days_remaining': round(days_remaining, 1) if days_remaining != 999 else 'N/A',
                'status': status
            })
            
        return {
            'report': inventory_report,
            'alerts': shortage_alerts,
            'restock_suggestions': restock_suggestions
        }

    # ==========================================
    # E. Fraud Detection
    # ==========================================
    @staticmethod
    def log_action(user_id, product_id, action_type, details=""):
        """Logs user action for recommendation mapping and behavior analysis."""
        db.execute_non_query(
            "INSERT INTO analytics_logs (user_id, product_id, action_type, action_details) "
            "VALUES (%s, %s, %s, %s)",
            [user_id, product_id, action_type, details]
        )

    @staticmethod
    def is_transaction_suspicious(user_id, shipping_address, total_amount):
        """
        Flags transactions that match fraud patterns:
        1. User checking out multiple orders in high velocity (e.g. >2 in last 5 mins).
        2. Unusually high dollar amount checkout (> $5,000).
        """
        # 1. Velocity check
        recent_orders_query = (
            "SELECT COUNT(*) as order_count FROM orders "
            "WHERE user_id = %s AND created_at >= datetime('now', '-5 minutes')" if db.db_type == 'sqlite' else
            "WHERE user_id = %s AND created_at >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)"
        )
        res = db.execute_query(recent_orders_query, [user_id])
        recent_count = res[0]['order_count'] if res else 0
        
        if recent_count >= 2:
            return True, "High purchase velocity detected (multiple checkouts in under 5 minutes)."
            
        # 2. Amount limit check
        if float(total_amount) > 5000.00:
            return True, "Transaction amount exceeds high-value threshold ($5,000)."
            
        return False, ""

    @staticmethod
    def detect_fraudulent_vendors():
        """
        Identifies vendors showing suspicious traits:
        1. Created products, but has overall rating <= 1.5.
        2. High rate of cancelled/refunded orders.
        """
        suspicious_vendors = db.execute_query(
            "SELECT v.id, v.business_name, u.username, v.rating, u.status "
            "FROM vendors v "
            "JOIN users u ON v.user_id = u.id "
            "WHERE v.rating > 0 AND v.rating <= 1.8 AND v.status = 'approved'"
        )
        
        # Check order cancellations
        cancelled_orders_ratio = db.execute_query(
            "SELECT oi.vendor_id, v.business_name, "
            "SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) * 1.0 / COUNT(o.id) as cancellation_rate "
            "FROM order_items oi "
            "JOIN orders o ON oi.order_id = o.id "
            "JOIN vendors v ON oi.vendor_id = v.id "
            "GROUP BY oi.vendor_id "
            "HAVING cancellation_rate > 0.40"
        )
        
        flags = []
        for v in suspicious_vendors:
            flags.append({
                'vendor_id': v['id'],
                'business_name': v['business_name'],
                'reason': f"Consistently poor product quality ratings (Average: {v['rating']}).",
                'action_suggested': 'block_vendor'
            })
            
        for c in cancelled_orders_ratio:
            flags.append({
                'vendor_id': c['vendor_id'],
                'business_name': c['business_name'],
                'reason': f"Extremely high order cancellation rate ({round(c['cancellation_rate']*100, 1)}%).",
                'action_suggested': 'review_orders'
            })
            
        return flags
