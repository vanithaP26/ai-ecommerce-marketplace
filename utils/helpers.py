import os
import re
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_username(username):
    # Alphanumeric, between 3 and 30 characters
    return username is not None and len(username) >= 3 and len(username) <= 30 and username.isalnum()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder_name='uploads'):
    """Saves uploaded product/logo image and returns the relative path."""
    if not file or not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    # Generate unique name to prevent duplicate overwrites
    unique_suffix = f"{uuid.uuid4().hex[:8]}_{int(time_nano())}" if 'time_nano' in globals() else f"{uuid.uuid4().hex[:8]}"
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{unique_suffix}{ext}"
    
    upload_dir = os.path.join(Config.get_upload_path(), folder_name)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    
    return f"uploads/{folder_name}/{unique_filename}"

def generate_invoice_html(order, user, order_items):
    """
    Generates a beautiful print-ready invoice HTML page saved in static/uploads/invoices/.
    Returns the relative path.
    """
    invoice_dir = os.path.join(Config.get_upload_path(), 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)
    
    invoice_filename = f"invoice_{order['id']}.html"
    invoice_path = os.path.join(invoice_dir, invoice_filename)
    
    items_rows = ""
    for idx, item in enumerate(order_items):
        total_price = item['price'] * item['quantity']
        items_rows += f"""
        <tr>
            <td>{idx + 1}</td>
            <td>{item['product_name']}</td>
            <td>${item['price']:.2f}</td>
            <td>{item['quantity']}</td>
            <td style="text-align: right;">${total_price:.2f}</td>
        </tr>
        """
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Invoice #{order['id']}</title>
        <style>
            body {{
                font-family: 'Inter', system-ui, sans-serif;
                color: #333;
                margin: 0;
                padding: 40px;
                background: #fdfdfd;
            }}
            .invoice-box {{
                max-width: 800px;
                margin: auto;
                padding: 30px;
                border: 1px solid #eee;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
                background: #fff;
                border-radius: 8px;
            }}
            .invoice-header {{
                display: flex;
                justify-content: space-between;
                border-bottom: 2px solid #6f42c1;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .company-details h2 {{
                color: #6f42c1;
                margin: 0 0 5px 0;
            }}
            .company-details p, .invoice-details p {{
                margin: 3px 0;
                font-size: 14px;
            }}
            .billing-details {{
                margin-bottom: 35px;
            }}
            .billing-details h3 {{
                color: #555;
                border-bottom: 1px solid #ddd;
                padding-bottom: 8px;
                margin-bottom: 12px;
            }}
            .billing-details p {{
                margin: 4px 0;
                font-size: 14px;
            }}
            .invoice-table {{
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                margin-bottom: 30px;
            }}
            .invoice-table th {{
                background: #f8f9fa;
                padding: 12px;
                font-size: 14px;
                color: #555;
                border-bottom: 2px solid #dee2e6;
            }}
            .invoice-table td {{
                padding: 12px;
                font-size: 14px;
                border-bottom: 1px solid #dee2e6;
            }}
            .total-section {{
                text-align: right;
                font-size: 16px;
                margin-top: 20px;
            }}
            .total-section .grand-total {{
                font-size: 22px;
                color: #6f42c1;
                font-weight: bold;
            }}
            .invoice-footer {{
                margin-top: 50px;
                border-top: 1px solid #eee;
                padding-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            .print-btn-container {{
                max-width: 800px;
                margin: 20px auto;
                text-align: right;
            }}
            .print-btn {{
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
            }}
            .print-btn:hover {{
                background-color: #59359a;
            }}
            @media print {{
                .print-btn-container {{
                    display: none;
                }}
                body {{
                    padding: 0;
                }}
                .invoice-box {{
                    box-shadow: none;
                    border: none;
                    padding: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="print-btn-container">
            <button class="print-btn" onclick="window.print()">Print Invoice</button>
        </div>
        <div class="invoice-box">
            <div class="invoice-header">
                <div class="company-details">
                    <h2>Nexus Market</h2>
                    <p>AI-Optimized Multi-Vendor eCommerce</p>
                    <p>support@nexusmarket.com</p>
                </div>
                <div class="invoice-details" style="text-align: right;">
                    <h3 style="margin: 0; color: #555;">INVOICE</h3>
                    <p><strong>Invoice #:</strong> INV-{order['id']:06d}</p>
                    <p><strong>Date:</strong> {order['created_at']}</p>
                    <p><strong>Order Status:</strong> {order['status'].upper()}</p>
                    <p><strong>Payment Status:</strong> {order['payment_status'].upper()}</p>
                </div>
            </div>
            
            <div class="billing-details">
                <h3>Bill To:</h3>
                <p><strong>{user['username']}</strong></p>
                <p>Email: {user['email']}</p>
                <p>Shipping Address:<br>{order['shipping_address'].replace('\n', '<br>')}</p>
            </div>
            
            <table class="invoice-table">
                <thead>
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th>Product Description</th>
                        <th style="width: 120px;">Unit Price</th>
                        <th style="width: 80px;">Qty</th>
                        <th style="width: 120px; text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows}
                </tbody>
            </table>
            
            <div class="total-section">
                <p>Subtotal: ${order['total_amount']:.2f}</p>
                <p>Shipping: $0.00</p>
                <p class="grand-total">Total Amount: ${order['total_amount']:.2f}</p>
            </div>
            
            <div class="invoice-footer">
                <p>Thank you for shopping with Nexus Market!</p>
                <p>This invoice is computer-generated and requires no signature.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(invoice_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    return f"uploads/invoices/{invoice_filename}"
