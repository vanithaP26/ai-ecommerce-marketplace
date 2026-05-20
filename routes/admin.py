from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db_manager import DatabaseManager
from services.ai_service import AIService
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__)
db = DatabaseManager()

# ==========================================
# 1. Admin Dashboard & Approvals
# ==========================================
@admin_bp.route('/admin/dashboard')
@admin_bp.route('/admin')
@admin_bp.route('/')
@admin_required
def dashboard():
    # Site Metrics
    stats = db.execute_query(
        "SELECT "
        "  (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE payment_status = 'paid') as total_sales, "
        "  (SELECT COUNT(*) FROM users WHERE role = 'customer') as customer_count, "
        "  (SELECT COUNT(*) FROM vendors) as vendor_count, "
        "  (SELECT COUNT(*) FROM products WHERE status = 'active') as product_count"
    )[0]
    
    # Vendor Approval Queue
    pending_vendors = db.execute_query(
        "SELECT v.*, u.username, u.email FROM vendors v "
        "JOIN users u ON v.user_id = u.id "
        "WHERE v.status = 'pending' "
        "ORDER BY v.created_at ASC"
    )
    
    # AI Fraud Alert logs
    fraud_logs = db.execute_query(
        "SELECT a.*, u.username FROM analytics_logs a "
        "LEFT JOIN users u ON a.user_id = u.id "
        "WHERE a.action_type IN ('fraud_flag', 'failed_login') "
        "ORDER BY a.created_at DESC LIMIT 10"
    )
    
    # AI Suspicious Vendor Detector
    suspicious_vendors = AIService.detect_fraudulent_vendors()
    
    # Sales Chart dataset
    sales_history = db.execute_query(
        "SELECT DATE(created_at) as date, SUM(total_amount) as total "
        "FROM orders WHERE payment_status = 'paid' "
        "GROUP BY DATE(created_at) ORDER BY date ASC LIMIT 15"
    )
    
    return render_template('admin/dashboard.html',
                           stats=stats,
                           pending_vendors=pending_vendors,
                           fraud_logs=fraud_logs,
                           suspicious_vendors=suspicious_vendors,
                           sales_history=sales_history)


# ==========================================
# 2. User Accounts Management
# ==========================================
@admin_bp.route('/admin/users')
@admin_required
def users():
    users_list = db.execute_query(
        "SELECT id, username, email, role, status, created_at FROM users WHERE role != 'admin' ORDER BY created_at DESC"
    )
    return render_template('admin/users.html', users=users_list)


@admin_bp.route('/admin/users/toggle_block/<int:user_id>', methods=['POST'])
@admin_required
def user_toggle_block(user_id):
    user_rows = db.execute_query("SELECT status, username FROM users WHERE id = %s", [user_id])
    if not user_rows:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
        
    user = user_rows[0]
    new_status = 'blocked' if user['status'] == 'active' else 'active'
    
    try:
        db.execute_non_query("UPDATE users SET status = %s WHERE id = %s", [new_status, user_id])
        
        # If user is a vendor, update vendor status too
        db.execute_non_query(
            "UPDATE vendors SET status = %s WHERE user_id = %s",
            ['blocked' if new_status == 'blocked' else 'approved', user_id]
        )
        
        flash(f"User '{user['username']}' status changed to '{new_status}'.", 'success')
    except Exception as e:
        flash('Could not update user status.', 'danger')
        print(f"[ADMIN USER STATUS UPDATE ERROR] {e}")
        
    return redirect(url_for('admin.users'))


# ==========================================
# 3. Vendor Accounts Management
# ==========================================
@admin_bp.route('/admin/vendors')
@admin_required
def vendors():
    vendors_list = db.execute_query(
        "SELECT v.*, u.username, u.email FROM vendors v "
        "JOIN users u ON v.user_id = u.id "
        "ORDER BY v.created_at DESC"
    )
    return render_template('admin/vendors.html', vendors=vendors_list)


@admin_bp.route('/admin/vendors/approve/<int:vendor_id>', methods=['POST'])
@admin_required
def vendor_approve(vendor_id):
    vendor_rows = db.execute_query("SELECT business_name FROM vendors WHERE id = %s", [vendor_id])
    if not vendor_rows:
        flash('Vendor not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    vendor = vendor_rows[0]
    
    try:
        db.execute_non_query("UPDATE vendors SET status = 'approved' WHERE id = %s", [vendor_id])
        flash(f"Vendor '{vendor['business_name']}' approved successfully!", 'success')
    except Exception as e:
        flash('Could not approve vendor.', 'danger')
        print(f"[ADMIN VENDOR APPROVE ERROR] {e}")
        
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/vendors/block/<int:vendor_id>', methods=['POST'])
@admin_required
def vendor_block(vendor_id):
    vendor_rows = db.execute_query("SELECT business_name, user_id FROM vendors WHERE id = %s", [vendor_id])
    if not vendor_rows:
        flash('Vendor not found.', 'danger')
        return redirect(url_for('admin.vendors'))
        
    vendor = vendor_rows[0]
    
    try:
        db.execute_non_query("UPDATE vendors SET status = 'blocked' WHERE id = %s", [vendor_id])
        # Also block user record
        db.execute_non_query("UPDATE users SET status = 'blocked' WHERE id = %s", [vendor['user_id']])
        flash(f"Vendor '{vendor['business_name']}' has been suspended and user account blocked.", 'success')
    except Exception as e:
        flash('Could not suspend vendor.', 'danger')
        print(f"[ADMIN VENDOR BLOCK ERROR] {e}")
        
    return redirect(url_for('admin.vendors'))
