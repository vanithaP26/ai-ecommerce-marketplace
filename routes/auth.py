from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
from models.db_manager import DatabaseManager
from utils.helpers import hash_password, verify_password, is_valid_email, is_valid_username

auth_bp = Blueprint('auth', __name__)
db = DatabaseManager()

# ==========================================
# Authentication Decorators
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'customer':
            flash('Access restricted to customers.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    return login_required(decorated_function)

def vendor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'vendor':
            flash('Access restricted to vendors.', 'danger')
            return redirect(url_for('user.index'))
        
        # Check vendor status
        vendor = db.execute_query(
            "SELECT status FROM vendors WHERE user_id = %s", [session['user_id']]
        )
        if not vendor:
            flash('Vendor profile not found.', 'danger')
            return redirect(url_for('user.index'))
            
        status = vendor[0]['status']
        if status == 'pending':
            flash('Your vendor registration is pending approval by the administration.', 'info')
            return redirect(url_for('user.index'))
        elif status == 'blocked':
            flash('Your vendor portal access has been suspended.', 'danger')
            return redirect(url_for('user.index'))
            
        return f(*args, **kwargs)
    return login_required(decorated_function)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access restricted to administrators.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    return login_required(decorated_function)


# ==========================================
# Routes
# ==========================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        role = request.form.get('role', 'customer') # 'customer' or 'vendor'
        
        # Vendor specific fields
        business_name = request.form.get('business_name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Basic validation
        if not username or not email or not password:
            flash('Please fill out all required fields.', 'danger')
            return render_template('auth/register.html')
            
        if not is_valid_username(username):
            flash('Username must be alphanumeric and between 3-30 characters.', 'danger')
            return render_template('auth/register.html')
            
        if not is_valid_email(email):
            flash('Invalid email address format.', 'danger')
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')
            
        if role == 'vendor' and not business_name:
            flash('Business name is required for vendor registration.', 'danger')
            return render_template('auth/register.html')
            
        # Check if username or email already exists
        user_check = db.execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s", [username, email]
        )
        if user_check:
            flash('Username or Email already registered.', 'danger')
            return render_template('auth/register.html')
            
        # For vendors, check if business name is unique
        if role == 'vendor':
            biz_check = db.execute_query(
                "SELECT id FROM vendors WHERE business_name = %s", [business_name]
            )
            if biz_check:
                flash('Business name already registered.', 'danger')
                return render_template('auth/register.html')
                
        # Insert user
        pw_hash = hash_password(password)
        try:
            user_id = db.execute_non_query(
                "INSERT INTO users (username, email, password_hash, role, status) "
                "VALUES (%s, %s, %s, %s, 'active')",
                [username, email, pw_hash, role]
            )
            
            # If Vendor, insert vendor profile
            if role == 'vendor':
                db.execute_non_query(
                    "INSERT INTO vendors (user_id, business_name, description, status) "
                    "VALUES (%s, %s, %s, 'pending')",
                    [user_id, business_name, description]
                )
                flash('Registration successful! Please wait for administration approval.', 'success')
            else:
                flash('Registration successful! Please log in.', 'success')
                
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"[AUTH REGISTRATION ERROR] {e}")
            
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'vendor':
            return redirect(url_for('vendor.dashboard'))
        return redirect(url_for('user.index'))
        
    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()  # can be username or email
        password = request.form.get('password')
        
        if not login_input or not password:
            flash('Please enter email/username and password.', 'danger')
            return render_template('auth/login.html')
            
        # Look up user by email or username
        user_rows = db.execute_query(
            "SELECT * FROM users WHERE email = %s OR username = %s", [login_input, login_input]
        )
        
        if not user_rows:
            flash('Invalid login credentials.', 'danger')
            return render_template('auth/login.html')
            
        user = user_rows[0]
        
        # Check if user is blocked
        if user['status'] == 'blocked':
            flash('Your account has been suspended by the administrator.', 'danger')
            return render_template('auth/login.html')
            
        # Brute-force check: check failed login attempts
        if user['failed_login_attempts'] >= 5:
            # Check if last failed login was less than 10 minutes ago
            last_failed = user['last_failed_login']
            if last_failed:
                # Handle datetime strings dynamically for safety (across databases)
                if isinstance(last_failed, str):
                    try:
                        last_failed_dt = datetime.strptime(last_failed, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # SQLite might store it slightly differently
                        last_failed_dt = datetime.strptime(last_failed.split('.')[0], '%Y-%m-%d %H:%M:%S')
                else:
                    last_failed_dt = last_failed
                    
                time_diff = (datetime.now() - last_failed_dt).total_seconds()
                if time_diff < 600:  # 10 minutes lockout
                    flash('Account locked due to too many failed attempts. Try again in 10 minutes.', 'danger')
                    return render_template('auth/login.html')
            
        # Verify Password
        if verify_password(user['password_hash'], password):
            # Login successful: Reset login attempts
            db.execute_non_query(
                "UPDATE users SET failed_login_attempts = 0, last_failed_login = NULL WHERE id = %s",
                [user['id']]
            )
            
            # Save user session
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            session.permanent = True
            
            flash(f"Welcome back, {user['username']}!", 'success')
            
            # Redirect to respective dashboard
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'vendor':
                # Check vendor status
                vendor = db.execute_query("SELECT status FROM vendors WHERE user_id = %s", [user['id']])
                if vendor and vendor[0]['status'] == 'approved':
                    return redirect(url_for('vendor.dashboard'))
                else:
                    session.clear()
                    flash('Your vendor portal is not approved yet.', 'warning')
                    return redirect(url_for('auth.login'))
                    
            return redirect(url_for('user.index'))
        else:
            # Login failed: Increment attempts
            new_attempts = user['failed_login_attempts'] + 1
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # If attempts hit 5, we can flag suspicious attempt
            db.execute_non_query(
                "UPDATE users SET failed_login_attempts = %s, last_failed_login = %s WHERE id = %s",
                [new_attempts, now_str, user['id']]
            )
            
            # Log to analytics for fraud audits
            db.execute_non_query(
                "INSERT INTO analytics_logs (user_id, action_type, action_details) "
                "VALUES (%s, 'failed_login', %s)",
                [user['id'], f"Failed login attempt from user. Attempt count: {new_attempts}"]
            )
            
            if new_attempts >= 5:
                flash('Account locked for 10 minutes due to 5 consecutive failed login attempts.', 'danger')
            else:
                flash('Invalid login credentials.', 'danger')
                
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('user.index'))
