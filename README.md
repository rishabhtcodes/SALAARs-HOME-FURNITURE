# SALAAR's HOME – Premium Furniture Showroom (Pure Django)

A full-featured, pure Django website rebuilt with pixel-level visual fidelity matching the original showroom experience, backed by PostgreSQL / SQLite, Django ORM, server-rendered Django Templates, and vanilla JavaScript.

---

## Features
- **Pure Django Architecture**: Zero React/Next.js/Node runtime dependency in production. Fast server-side HTML rendering.
- **Identical Visual Design**: Tailored luxury typography (`Cormorant Garamond` & `Inter`), custom gold/cream/ink design system, responsive layouts across mobile, tablet, and desktop.
- **Storefront & Catalog**:
  - Full catalog browsing with instant sidebar filtering by price range, delivery, and special tags.
  - Category navigation bar matching original sticky category scroller.
  - Instant live search overlay with debounced API responses.
  - Product details page with multi-image gallery switching, specifications, and related pieces.
- **E-Commerce & Checkout**:
  - Session-based & authenticated shopping cart.
  - Server-side inventory, price calculation, and order placement.
  - User registration, authentication, and order history dashboard.
  - Full Django Admin suite for managing products, categories, orders, and inquiries.

---

## Quick Start / Local Setup

### 1. Requirements
- Python 3.10+
- (Optional) PostgreSQL

### 2. Environment Setup
```bash
# Clone the repository and enter the directory
cd SALAARs-HOME-FURNITURE

# (Recommended) Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Database & Migrations
```bash
# Copy environment configuration
cp .env.example .env

# Run database migrations
python manage.py migrate

# Seed catalog (Categories, Nav Collections, 100 Products)
python manage.py seed_store

# Collect static assets
python manage.py collectstatic --noinput
```

### 4. Create Admin Account
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## Running Automated Tests
```bash
python manage.py test
```

---

## PostgreSQL Configuration (Optional)
In your `.env` file, specify:
```env
DATABASE_URL=postgres://your_user:your_password@localhost:5432/salaars_furniture
```
Then run `python manage.py migrate` and `python manage.py seed_store`.
