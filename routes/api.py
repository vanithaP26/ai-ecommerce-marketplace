from flask import Blueprint, jsonify, request, session
from models.db_manager import DatabaseManager
from services.ai_service import AIService
from routes.auth import login_required
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)
db = DatabaseManager()

# ==========================================
# 1. Search Auto-Suggestions
# ==========================================
@api_bp.route('/api/search/suggestions')
def suggestions():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
        
    suggestions_list = AIService.get_search_suggestions(q, limit=5)
    return jsonify(suggestions_list)


# ==========================================
# 2. AJAX Cart Helper
# ==========================================
@api_bp.route('/api/cart/count')
def cart_count():
    user_id = session.get('user_id')
    if not user_id or session.get('role') != 'customer':
        return jsonify({'count': 0})
        
    res = db.execute_query("SELECT SUM(quantity) as total_qty FROM cart WHERE user_id = %s", [user_id])
    count = res[0]['total_qty'] if res and res[0]['total_qty'] else 0
    return jsonify({'count': count})


# ==========================================
# 3. Sales Forecast Datasets for Chart.js
# ==========================================
@api_bp.route('/api/sales/forecast-data')
@login_required
def forecast_data():
    user_id = session['user_id']
    role = session['role']
    
    vendor_id = None
    if role == 'vendor':
        vendor_rows = db.execute_query("SELECT id FROM vendors WHERE user_id = %s", [user_id])
        if not vendor_rows:
            return jsonify({'error': 'Vendor details missing'}), 400
        vendor_id = vendor_rows[0]['id']
    elif role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Get sales history and forecasts (past 30 days history + 30 days forecast)
    forecast_results = AIService.get_sales_forecast(vendor_id, days=30)
    history = forecast_results['history']
    
    # Process history
    labels = []
    revenue_history = []
    volume_history = []
    
    for entry in history:
        # Check type of date
        if isinstance(entry['date'], str):
            date_str = entry['date']
        else:
            date_str = entry['date'].strftime('%Y-%m-%d')
        labels.append(date_str)
        revenue_history.append(float(entry['revenue']))
        volume_history.append(int(entry['volume']))
        
    # Generate forecast labels and linear projections
    forecast_labels = list(labels)  # Start with past labels
    forecast_revenue = list(revenue_history)
    
    # Get slope and intercept for projections
    n = len(history)
    if n >= 3:
        # Reconstruct slope and intercept to project sequential steps
        x = list(range(n))
        y_rev = [float(s['revenue']) for s in history]
        
        sum_x = sum(x)
        sum_y = sum(y_rev)
        sum_xx = sum(xv * xv for xv in x)
        sum_xy = sum(xv * yv for xv, yv in zip(x, y_rev))
        denominator = (n * sum_xx - sum_x * sum_x)
        
        if denominator != 0:
            m = (n * sum_xy - sum_x * sum_y) / denominator
            c = (sum_y - m * sum_x) / n
            
            # Predict next 10 days day-by-day for a smoother chart line
            last_date = datetime.strptime(labels[-1], '%Y-%m-%d') if labels else datetime.now()
            
            for i in range(n, n + 10):
                future_date = (last_date + timedelta(days=(i - n + 1))).strftime('%Y-%m-%d')
                projected_val = max(m * i + c, 0.0)
                
                forecast_labels.append(future_date)
                forecast_revenue.append(round(projected_val, 2))
                
    return jsonify({
        'history_labels': labels,
        'history_revenue': revenue_history,
        'history_volume': volume_history,
        'forecast_labels': forecast_labels,
        'forecast_revenue': forecast_revenue,
        'trend': forecast_results['trend'],
        'predicted_revenue': round(forecast_results['predicted_revenue_next_period'], 2),
        'predicted_volume': forecast_results['predicted_volume_next_period']
    })
