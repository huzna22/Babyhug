<h1 align="center">
  <img src="https://img.shields.io/badge/Baby%20Hug-%F0%9F%91%B6-D9933B?style=for-the-badge" alt="Baby Hug"/>
</h1>

<p align="center">
  <strong>Premium Organic Baby-wear E-Commerce Platform</strong><br/>
  Built with Python · Django · MySQL · Tailwind CSS
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-5.1.4-092E20?style=flat&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/TailwindCSS-3.x-06B6D4?style=flat&logo=tailwindcss&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-Academic-green?style=flat"/>
</p>

---

## 📖 About

**Baby Hug** is a full-featured e-commerce web application for premium organic baby dresses, rompers, shoes, and accessories targeting parents of children aged 0–4 years.

Key highlights:
- 🧵 Products browsable by **category**, **age group**, and **price range**
- 🛒 Full **cart & wishlist** management
- 💳 **Checkout** with saved addresses and multiple payment methods (UPI, Card, Net Banking, COD)
- 📦 **Order tracking** with real-time status timeline
- ⭐ **Review system** with admin moderation
- 👤 Complete **user profile** management (personal info, password, addresses)
- 🔐 **Django Admin** panel for full back-office control

---

## 🖥️ Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.11, Django 5.1.4           |
| Database    | SQLite (dev) / MySQL 8.0 (prod)     |
| Frontend    | HTML5, Tailwind CSS (CDN), Vanilla JS |
| Typography  | EB Garamond + Manrope (Google Fonts)|
| Icons       | Google Material Symbols             |
| Auth        | Django's built-in auth system       |
| Images      | Pillow (Django ImageField)          |

---

## ⚙️ Prerequisites

Make sure the following are installed on your system before running the project:

- **Python 3.10+** → https://www.python.org/downloads/
- **pip** (comes with Python)
- **MySQL 8.0+** *(only for production setup)* → https://dev.mysql.com/downloads/installer/
- **Git** *(optional)* → https://git-scm.com/

---

## 🚀 Local Installation & Setup

### Step 1 — Clone / Download the Project

```bash
# If using Git
git clone <your-repo-url>
cd babyhug2.0

# OR just navigate to the project folder
cd "c:\Users\HUZNA SHAJAHAN\OneDrive\Desktop\babyhug2.0"
```

### Step 2 — Create a Virtual Environment *(recommended)*

```bash
# Create venv
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `Django==5.1.4`
- `mysqlclient==2.3.0`
- `Pillow==11.1.0`

### Step 4 — Configure the Database

#### Option A — SQLite (Development, Zero Setup)

The project is already configured to use **SQLite** out of the box.  
No extra steps needed — skip directly to Step 5.

#### Option B — MySQL (Production / Preferred)

1. **Create the database** in MySQL:
   ```sql
   CREATE DATABASE babyhug_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Update `babyhug/settings.py`** — uncomment the MySQL block and comment out the SQLite block:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'babyhug_db',
           'USER': 'root',           # your MySQL username
           'PASSWORD': 'your_pass',  # your MySQL password
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {'charset': 'utf8mb4'},
       }
   }
   ```

### Step 5 — Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates all 13 database tables automatically.

### Step 6 — Create an Admin Superuser

```bash
python manage.py createsuperuser
```

Enter your preferred email, and password when prompted.

> **Quick shortcut** — A default admin is seeded if you run the seed script below.

### Step 7 — Load Sample Data *(Optional)*

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from store.models import Profile, Category, Product

# Admin user
if not User.objects.filter(username='admin@babyhug.in').exists():
    u = User.objects.create_superuser('admin@babyhug.in','admin@babyhug.in','Admin@1234',first_name='Admin',last_name='BabyHug')
    Profile.objects.create(user=u, phone='9876543210')

# Categories
for name, slug, desc in [
    ('Baby Dresses','baby-dresses','Frocks & Gowns'),
    ('Rompers & Sets','rompers-sets','Bodysuits & Sets'),
    ('Baby Shoes','baby-shoes','Booties & Pre-Walkers'),
    ('Accessories','accessories','Bibs & Headbands'),
    ('Toys & Keepsakes','toys','Organic Plushies'),
    ('Baby Tops','baby-tops','T-Shirts & Kurtis'),
]:
    Category.objects.get_or_create(slug=slug, defaults={'name':name,'description':desc,'is_active':True})
print('Sample data loaded!')
"
```

### Step 8 — Run the Development Server

```bash
python manage.py runserver
```

Open your browser and visit: **http://127.0.0.1:8000**

---

## 🔑 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@babyhug.in` | `Admin@1234` |
| Admin Panel | http://127.0.0.1:8000/admin/ | Same as above |

> ⚠️ **Change the admin password before deploying to production!**

---

## 🌐 All Pages & Routes

| Page | URL | Auth Required |
|------|-----|:---:|
| 🏠 Home | `/` | No |
| 🛍️ All Products | `/products/` | No |
| 📦 Product Detail | `/products/<slug>/` | No |
| 🛒 Shopping Cart | `/cart/` | ✅ Yes |
| ❤️ Wishlist | `/wishlist/` | ✅ Yes |
| 💳 Checkout | `/checkout/` | ✅ Yes |
| ✅ Order Confirmation | `/order/confirmation/<id>/` | ✅ Yes |
| 📋 My Orders | `/orders/` | ✅ Yes |
| 🔍 Order Detail | `/orders/<id>/` | ✅ Yes |
| 👤 My Profile | `/profile/` | ✅ Yes |
| 🔑 Sign In | `/login/` | No |
| 📝 Register | `/register/` | No |
| 📩 Contact | `/contact/` | No |
| ⚙️ Admin Panel | `/admin/` | ✅ Staff |

---

## 🗄️ Database Schema (13 Models)

```
Profile          → extends User with phone, blocked status
Address          → delivery addresses (Home/Work/Other)
Category         → product categories with slug & image
Product          → items with price, stock, colour, age_group
ProductImage     → extra gallery images per product
Cart             → one cart per user
CartItem         → cart line items with quantity
Wishlist         → saved products per user
Order            → order master (Pending→Delivered)
OrderItem        → order line items with snapshot price
Payment          → payment record (UPI/Card/COD/NetBanking)
Review           → star ratings + text with approval workflow
Feedback         → contact form submissions
```

---

## 📁 Project Structure

```
babyhug2.0/
├── babyhug/
│   ├── settings.py           ← App settings (DB, static, auth)
│   ├── urls.py               ← Root URL configuration
│   └── wsgi.py
├── store/
│   ├── migrations/           ← Database migration files
│   ├── models.py             ← All 13 database models
│   ├── views.py              ← All view logic (30+ functions)
│   ├── urls.py               ← URL patterns (20 routes)
│   ├── admin.py              ← Django admin configuration
│   └── context_processors.py ← Global cart/wishlist counts
├── templates/
│   ├── base.html             ← Master layout (header/footer/nav)
│   └── store/
│       ├── home.html
│       ├── product_list.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── wishlist.html
│       ├── checkout.html
│       ├── order_confirmation.html
│       ├── order_detail.html
│       ├── my_orders.html
│       ├── profile.html
│       ├── login.html
│       ├── register.html
│       ├── contact.html
│       └── partials/
│           ├── product_card.html
│           └── address_fields.html
├── static/
│   ├── css/
│   └── js/
├── media/                    ← Uploaded product images
├── requirements.txt
├── manage.py
└── README.md
```

---

## 🖼️ Adding Product Images

1. Start the server and go to **http://127.0.0.1:8000/admin/**
2. Log in with the admin credentials
3. Navigate to **Store → Products**
4. Click any product → scroll to **Image** field → upload a `.jpg` / `.png`
5. Save — the image will appear across the site automatically

---

## 🧪 Running Checks

```bash
# Check for any configuration issues
python manage.py check

# Run all system checks with deployment flag
python manage.py check --deploy
```

---

## 🔒 Production Checklist

Before deploying to a live server:

- [ ] Set `DEBUG = False` in `settings.py`
- [ ] Set a strong `SECRET_KEY` (never use the default)
- [ ] Switch `DATABASES` to MySQL
- [ ] Set `ALLOWED_HOSTS = ['yourdomain.com']`
- [ ] Run `python manage.py collectstatic`
- [ ] Use **Gunicorn** + **Nginx** for serving
- [ ] Change the default admin password

---

## 👩‍💻 Author

**Huzna Shajahan**  
MCA – Mini Project  
Baby Hug E-Commerce Platform

---

## 📄 License

This project is submitted as an academic mini-project. All rights reserved © 2024 Huzna Shajahan.
