# Nexus Market: AI-Powered Multi-Vendor eCommerce Marketplace

A modern, full-stack, responsive multi-vendor marketplace platform featuring intelligent search typo correction, personalized recommendation scorings, predictive sales forecasting, automated inventory alerts, and transaction velocity fraud analysis.

Suitable for final year projects, placement portfolios, and production deployment.

## 🚀 Key Features

### 1. Multi-Vendor Ecosystem
- **Separate Portals:** Distinct dashboards for Customers, Vendors, and Site Administrators.
- **Vendor Onboarding:** Pending vendor registration queue with manual Admin approval workflow.
- **Inventory Management:** Vendors can add, edit, or delete items, upload product photos, and track stock.
- **Customer Reviews:** Verified purchase feedback system showing average rating badges.

### 2. AI & Data Analytics Services
- **Intelligent Search Suggestions:** Auto-suggestions using prefix match caches.
- **Typo Spellcheck:** Levenshtein distance matching query terms against actual product naming tokens.
- **Sales Forecasts:** Ordinary Least Squares linear regression charting past 30 days and predicting 10-day revenues.
- **Inventory Shortage suggestions:** Analyzes sales velocity and stock quantities to suggest exact restock numbers.
- **Fraud Velocity Audits:** Identifies credential attacks and large transactions occurring in tight time slots.

### 3. Core E-Commerce Flows
- Interactive product comparison grid (up to 3 products side-by-side).
- Shopping cart with AJAX count badges.
- Wishlist toggles.
- Dynamic PDF-ready HTML invoice generation on checkout.

---

## 🛠️ Technology Stack
- **Frontend:** HTML5, CSS3 (Vanilla Custom Theme), JavaScript (Vanilla JS, Chart.js for visualization).
- **Backend:** Python 3.10+ (Flask framework, Blueprint routing).
- **Database:** Dual-mode handling supporting SQLite (Default Local Dev) and MySQL (Production-ready).

---

## 📁 Project Directory Structure
```text
multi_vendor_marketplace/
│
├── app.py                  # Application factory entry point
├── config.py               # Environment configuration settings
├── database.sql            # Core database schema definitions
├── requirements.txt        # Python dependency specifications
├── run_tests.py            # Local verification test suite
│
├── models/
│   └── db_manager.py       # Dual SQL database connector & caching
│
├── routes/
│   ├── auth.py             # User sign-in, signup and logout blueprints
│   ├── user.py             # Browsing, cart, checkout & customer routes
│   ├── vendor.py           # Catalog management & analytics panels
│   ├── admin.py            # Platform metrics & vendor approvals
│   └── api.py              # AJAX Suggestions, cart count, forecast API feeds
│
├── services/
│   └── ai_service.py       # AI models & analytics telemetry
│
├── static/
│   ├── css/
│   │   └── styles.css      # Dark/Light responsive design stylesheet
│   ├── js/
│   │   ├── app.js          # Core app script (Theme, debounce suggestions)
│   │   └── dashboards.js   # Analytics charts (Chart.js renderer)
│   └── uploads/
│       └── products/       # Vendor uploaded product image directories
│
├── templates/
│   ├── layouts/
│   │   └── base.html       # Base layout navbar and footer structures
│   ├── auth/               # Login & Register views
│   ├── user/               # Customer dashboard/storefront views
│   ├── vendor/             # Vendor control views
│   ├── admin/              # Site admin control views
│   └── errors/             # Custom 404 & 500 pages
```

---

## 💻 Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- Pip (Python Package Installer).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify System Tests
To check that the database schema creation, table mappings, and seeds are fully functional:
```bash
python run_tests.py
```

### 4. Start the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 🔑 Seeding / Testing Accounts
The application automatically seeds initial data if the database is empty:
- **Site Administrator:**
  - Email: `admin@nexusmarket.com`
  - Password: `admin123`
- **Active Vendor:**
  - Email: `vendor@tech.com`
  - Password: `vendor123` (Gizmo Tech Store)
- **Pending Vendor (For approval testing):**
  - Email: `vendor@fashion.com`
  - Password: `vendor123` (Vogue Outfitters)
