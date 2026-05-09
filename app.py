# WARNING: Intentionally vulnerable. Local testing only. Never deploy.

from flask import Flask, request, render_template_string, render_template, redirect, url_for, session, jsonify, make_response, send_from_directory
import sqlite3
import subprocess
import time
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import jwt
import threading
import pickle
import base64
import random
from database import init_db, get_db_connection
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
app.secret_key = 'vulnerable_secret_key_123'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
init_db()

# HTML Base template with placeholder for content
def get_base_template():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VulnShop - {% block title %}Online Shopping{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        :root {
            --amazon-dark: #131921;
            --amazon-light: #232f3e;
            --amazon-orange: #febd69;
            --amazon-blue: #007185;
            --amazon-yellow: #ffd814;
            --flipkart-blue: #2874f0;
            --flipkart-yellow: #ffe11b;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: #eaeded;
            min-height: 100vh;
        }
        
        /* Header - Amazon Style */
        .header {
            background: linear-gradient(135deg, var(--amazon-dark) 0%, var(--amazon-light) 100%);
            padding: 8px 20px;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        
        .header-brand {
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .header-brand:hover {
            color: var(--amazon-orange);
        }
        
        .header-brand .tagline {
            font-size: 0.75rem;
            font-weight: 400;
            color: #ccc;
            margin-top: -5px;
        }
        
        .search-box {
            flex: 1;
            max-width: 700px;
            margin: 0 20px;
        }
        
        .search-box .input-group {
            border-radius: 8px;
            overflow: hidden;
        }
        
        .search-box input {
            border: none;
            padding: 12px 15px;
            font-size: 1rem;
        }
        
        .search-box .btn-search {
            background: var(--amazon-orange);
            border: none;
            color: #131921;
            padding: 12px 20px;
            font-weight: 600;
        }
        
        .search-box .btn-search:hover {
            background: #f3a847;
        }
        
        .header-nav {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .header-nav a {
            color: white;
            text-decoration: none;
            font-size: 0.9rem;
            padding: 8px 12px;
            border-radius: 4px;
            transition: all 0.2s;
        }
        
        .header-nav a:hover {
            background: rgba(255,255,255,0.1);
            color: var(--amazon-orange);
        }
        
        .header-nav .cart-icon {
            position: relative;
            font-size: 1.5rem;
        }
        
        .header-nav .cart-count {
            position: absolute;
            top: -8px;
            right: -8px;
            background: var(--amazon-orange);
            color: #131921;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 50%;
        }
        
        /* Sub Navigation */
        .sub-nav {
            background: var(--amazon-light);
            padding: 8px 20px;
            display: flex;
            gap: 25px;
            border-bottom: 1px solid #37475a;
        }
        
        .sub-nav a {
            color: #ddd;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: color 0.2s;
        }
        
        .sub-nav a:hover {
            color: white;
        }
        
        /* Main Content */
        main {
            max-width: 1500px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Product Cards - Amazon Style */
        .product-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s ease;
            height: 100%;
            border: 1px solid #ddd;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .product-card .product-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
            background: #f7f7f7;
        }
        
        .product-card .card-body {
            padding: 15px;
        }
        
        .product-card .product-title {
            font-size: 1rem;
            font-weight: 600;
            color: #0f1111;
            margin-bottom: 8px;
            line-height: 1.4;
            height: 2.8em;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        
        .product-card .product-rating {
            color: #ffa41c;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .product-card .product-reviews {
            color: #007185;
            font-size: 0.85rem;
            margin-left: 5px;
        }
        
        .product-card .product-price {
            font-size: 1.4rem;
            font-weight: 700;
            color: #b12704;
            margin: 10px 0;
        }
        
        .product-card .product-price .currency {
            font-size: 0.8rem;
            vertical-align: top;
        }
        
        .product-card .prime-badge {
            color: #00a8e1;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .btn-amazon {
            background: linear-gradient(180deg, #ffd814 0%, #ffc107 100%);
            border: 1px solid #fcd200;
            color: #0f1111;
            border-radius: 20px;
            padding: 8px 20px;
            font-weight: 600;
            width: 100%;
            transition: all 0.2s;
        }
        
        .btn-amazon:hover {
            background: linear-gradient(180deg, #f7ca00 0%, #f0b800 100%);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #232f3e 0%, #131921 50%, #febd69 100%);
            padding: 60px 40px;
            margin: -20px -20px 30px;
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .hero-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.03' fill-rule='evenodd'/%3E%3C/svg%3E");
        }
        
        .hero-banner .container {
            position: relative;
            z-index: 1;
        }
        
        .hero-banner h1 {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Category Section */
        .category-section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0f1111;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--amazon-orange);
        }
        
        /* Footer - Amazon Style */
        .footer {
            background: var(--amazon-dark);
            color: white;
            padding: 50px 0 30px;
            margin-top: 50px;
        }
        
        .footer-back-to-top {
            background: var(--amazon-light);
            text-align: center;
            padding: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .footer-back-to-top:hover {
            background: #37475a;
        }
        
        .footer h5 {
            color: white;
            font-weight: 700;
            margin-bottom: 15px;
            font-size: 1rem;
        }
        
        .footer a {
            color: #ddd;
            text-decoration: none;
            display: block;
            margin-bottom: 8px;
            font-size: 0.9rem;
            transition: color 0.2s;
        }
        
        .footer a:hover {
            color: var(--amazon-orange);
        }
        
        .footer-bottom {
            border-top: 1px solid #3a4553;
            margin-top: 40px;
            padding-top: 30px;
            text-align: center;
        }
        
        /* Forms */
        .form-control {
            border: 1px solid #a6a6a6;
            border-radius: 4px;
            padding: 10px 12px;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .form-control:focus {
            border-color: #e77600;
            box-shadow: 0 0 3px rgba(231, 118, 0, 0.5);
        }
        
        /* Cards */
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* Tables */
        .table thead th {
            background: var(--amazon-light);
            color: white;
            font-weight: 600;
            border: none;
        }
        
        /* Buttons */
        .btn {
            border-radius: 4px;
            font-weight: 600;
            padding: 8px 16px;
        }
        
        /* Badges */
        .badge {
            padding: 5px 10px;
            border-radius: 4px;
        }
        
        .badge-amazon {
            background: var(--amazon-orange);
            color: #131921;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="d-flex align-items-center justify-content-between">
            <a class="header-brand" href="/">
                <i class="bi bi-shop-window"></i>
                <div>
                    VulnShop
                    <div class="tagline">Vulnerable Testing Environment</div>
                </div>
            </a>
            
            <form class="search-box" action="/search" method="get">
                <div class="input-group">
                    <input type="text" name="q" class="form-control" placeholder="Search products, categories...">
                    <button class="btn btn-search" type="submit"><i class="bi bi-search"></i></button>
                </div>
            </form>
            
            <div class="header-nav">
                <a href="/dashboard"><i class="bi bi-person"></i> Account</a>
                <a href="/track-order"><i class="bi bi-truck"></i> Orders</a>
                <a href="/checkout" class="cart-icon">
                    <i class="bi bi-cart3"></i>
                    <span class="cart-count">{{ session.get('cart_count', 0) }}</span>
                </a>
                {% if session.get('user_id') %}
                    <a href="/logout"><i class="bi bi-box-arrow-right"></i> Logout</a>
                {% else %}
                    <a href="/login"><i class="bi bi-box-arrow-in-right"></i> Login</a>
                {% endif %}
            </div>
        </div>
    </header>
    
    <!-- Sub Navigation -->
    <nav class="sub-nav">
        <a href="/">All</a>
        <a href="/search?q=Electronics">Electronics</a>
        <a href="/search?q=Clothing">Clothing</a>
        <a href="/search?q=Accessories">Accessories</a>
        <a href="/support">Customer Service</a>
        <a href="/admin" style="margin-left: auto; color: #ff6b6b;"><i class="bi bi-shield-lock"></i> Admin</a>
    </nav>
    
    <main>
        {{ content|safe }}
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="footer-back-to-top" onclick="window.scrollTo(0,0)">
            <span>Back to top</span>
        </div>
        <div class="container">
            <div class="row">
                <div class="col-md-3">
                    <h5>Get to Know Us</h5>
                    <a href="/support">About VulnShop</a>
                    <a href="/support">Careers</a>
                    <a href="/support">Press Releases</a>
                </div>
                <div class="col-md-3">
                    <h5>Connect with Us</h5>
                    <a href="/support">Facebook</a>
                    <a href="/support">Twitter</a>
                    <a href="/support">Instagram</a>
                </div>
                <div class="col-md-3">
                    <h5>Make Money with Us</h5>
                    <a href="/support">Sell on VulnShop</a>
                    <a href="/support">Become an Affiliate</a>
                    <a href="/support">Advertise</a>
                </div>
                <div class="col-md-3">
                    <h5>Let Us Help You</h5>
                    <a href="/support">Help</a>
                    <a href="/track-order">Track Orders</a>
                    <a href="/support">Returns</a>
                    <a href="/support">Customer Service</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p class="mb-2">&copy; 2024 VulnShop. Intentionally vulnerable for testing.</p>
                <p class="text-muted small mb-0">WARNING: This is a deliberately vulnerable application for security testing only. Never deploy to production.</p>
            </div>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Home / Product listing
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    html = get_base_template().replace('{{ content|safe }}', '''
<!-- Hero Banner -->
<div class="hero-banner">
    <div class="container text-center">
        <h1>Welcome to VulnShop</h1>
        <p class="lead">Intentionally vulnerable e-commerce for security testing</p>
    </div>
</div>

<!-- Deals Section -->
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-lightning-charge-fill text-warning"></i> Today's Deals</h2>
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        {% for product in products %}
        <div class="col">
            <div class="card h-100 product-card">
                <img src="{{ product.image_url }}" class="product-image" alt="{{ product.name }}">
                <div class="card-body">
                    <h5 class="product-title">{{ product.name }}</h5>
                    <div class="product-rating">
                        {% for i in range(5) %}
                            {% if i < product.rating|int %}
                                <i class="bi bi-star-fill"></i>
                            {% else %}
                                <i class="bi bi-star"></i>
                            {% endif %}
                        {% endfor %}
                        <span class="product-reviews">{{ product.reviews }}</span>
                    </div>
                    <div class="product-price">
                        <span class="currency">$</span>{{ "%.2f"|format(product.price) }}
                    </div>
                    <div class="prime-badge">
                        <i class="bi bi-check-circle-fill"></i> prime <span style="color: #00a8e1; font-weight: 600;">FREE Delivery</span>
                    </div>
                    <a href="/product?id={{ product.id }}" class="btn btn-amazon">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<!-- Categories -->
<div class="row g-4">
    <div class="col-md-4">
        <div class="category-section h-100">
            <h3 class="section-title">Electronics</h3>
            <p>Discover the latest gadgets and tech accessories</p>
            <a href="/search?q=Electronics" class="btn btn-outline-primary">Shop Now</a>
        </div>
    </div>
    <div class="col-md-4">
        <div class="category-section h-100">
            <h3 class="section-title">Clothing</h3>
            <p>Fashion for every occasion at great prices</p>
            <a href="/search?q=Clothing" class="btn btn-outline-primary">Shop Now</a>
        </div>
    </div>
    <div class="col-md-4">
        <div class="category-section h-100">
            <h3 class="section-title">Accessories</h3>
            <p>Complete your look with premium accessories</p>
            <a href="/search?q=Accessories" class="btn btn-outline-primary">Shop Now</a>
        </div>
    </div>
</div>
''')
    return render_template_string(html, products=products)

# 1. SQL Injection - /product?id=
@app.route('/product')
def product():
    product_id = request.args.get('id', '')
    
    # Check for time-based blind SQL injection
    if 'SLEEP(5)' in product_id.upper() or 'WAITFOR DELAY' in product_id.upper():
        time.sleep(5)
    
    conn = None
    try:
        conn = get_db_connection()
        # VULNERABLE: Raw string formatting - SQL Injection
        query = f"SELECT * FROM products WHERE id = {product_id}"
        cursor = conn.execute(query)
        product = cursor.fetchone()
        
        if product:
            html = get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="/">Home</a></li>
            <li class="breadcrumb-item"><a href="/search?q={{ product.category }}">{{ product.category }}</a></li>
            <li class="breadcrumb-item active">{{ product.name }}</li>
        </ol>
    </nav>
</div>

<div class="row g-4">
    <div class="col-md-5">
        <div class="category-section">
            <img src="{{ product.image_url }}" class="img-fluid rounded" style="width: 100%; max-height: 400px; object-fit: cover;" alt="{{ product.name }}">
        </div>
    </div>
    <div class="col-md-7">
        <div class="category-section h-100">
            <h1 style="font-size: 1.5rem; font-weight: 600;">{{ product.name }}</h1>
            <div class="product-rating mb-3">
                {% for i in range(5) %}
                    {% if i < product.rating|int %}
                        <i class="bi bi-star-fill"></i>
                    {% else %}
                        <i class="bi bi-star"></i>
                    {% endif %}
                {% endfor %}
                <span class="product-reviews">{{ product.reviews }} ratings</span>
            </div>
            <hr>
            <div class="product-price mb-3" style="font-size: 1.8rem;">
                <span class="currency">$</span>{{ "%.2f"|format(product.price) }}
            </div>
            <div class="prime-badge mb-3">
                <i class="bi bi-check-circle-fill"></i> prime <span style="color: #00a8e1; font-weight: 600;">FREE Delivery</span> <span class="text-muted">Tomorrow</span>
            </div>
            <p class="text-muted mb-4">{{ product.description }}</p>
            <div class="d-grid gap-2 d-md-flex">
                <a href="/checkout" class="btn btn-amazon btn-lg">Add to Cart</a>
                <a href="/checkout" class="btn btn-success btn-lg">Buy Now</a>
            </div>
            <div class="mt-4">
                <p class="small text-muted mb-1"><i class="bi bi-shield-check"></i> Secure transaction</p>
                <p class="small text-muted mb-1"><i class="bi bi-arrow-return-left"></i> 30-day return policy</p>
                <p class="small text-muted mb-0"><i class="bi bi-truck"></i> Ships from VulnShop</p>
            </div>
        </div>
    </div>
</div>
''')
            return render_template_string(html, product=product)
        else:
            return "Product not found", 404
            
    except sqlite3.Error as e:
        # Return MySQL-like error for SQL injection detection
        error_msg = str(e)
        if "'" in product_id or '"' in product_id or '\\' in product_id:
            return f"<html><body><h3>Error</h3><p>mysqli_query(): {error_msg}</p><p>You have an error in your SQL syntax; check the manual...</p></body></html>", 500
        return f"Error: {error_msg}", 500
    finally:
        if conn:
            conn.close()

# 2. XSS - /search?q=
@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    products = []
    conn = None
    try:
        conn = get_db_connection()
        if query:
            # Also vulnerable SQL injection in search
            search_query = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%' OR category LIKE '%{query}%'"
            products = conn.execute(search_query).fetchall()
        else:
            products = conn.execute('SELECT * FROM products').fetchall()
    except:
        pass
    finally:
        if conn:
            conn.close()
    
    # VULNERABLE: Raw query output without encoding - XSS
    html = get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title">Search Results for: <span style="color: #b12704;">''' + query + '''</span></h2>
    
    {% if products %}
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        {% for product in products %}
        <div class="col">
            <div class="card h-100 product-card">
                <img src="{{ product.image_url }}" class="product-image" alt="{{ product.name }}">
                <div class="card-body">
                    <h5 class="product-title">{{ product.name }}</h5>
                    <div class="product-rating">
                        {% for i in range(5) %}
                            {% if i < product.rating|int %}
                                <i class="bi bi-star-fill"></i>
                            {% else %}
                                <i class="bi bi-star"></i>
                            {% endif %}
                        {% endfor %}
                        <span class="product-reviews">{{ product.reviews }}</span>
                    </div>
                    <div class="product-price">
                        <span class="currency">$</span>{{ "%.2f"|format(product.price) }}
                    </div>
                    <div class="prime-badge">
                        <i class="bi bi-check-circle-fill"></i> prime <span style="color: #00a8e1; font-weight: 600;">FREE Delivery</span>
                    </div>
                    <a href="/product?id={{ product.id }}" class="btn btn-amazon">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
        <div class="alert alert-info">
            <i class="bi bi-info-circle"></i> No products found matching your search. Try different keywords.
        </div>
    {% endif %}
</div>
''')
    return render_template_string(html, products=products)

# 3. LFI - /support?file=
@app.route('/support')
def support():
    filename = request.args.get('file', 'help.txt')
    
    # VULNERABLE: Local File Inclusion
    if '../../../../etc/passwd' in filename or '..\\..\\..\\etc\\passwd' in filename:
        return """root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin""", 200
    
    if '..\\..\\..\\windows\\win.ini' in filename or '../../../windows/win.ini' in filename:
        return """; for 16-bit app support
[fonts]
[extensions]
[mci extensions]
[files]
[Mail]
""", 200
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-headset"></i> Customer Support</h2>
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <p class="text-muted mb-4">Need help? Browse our help documentation or contact us.</p>
            
            <div class="card">
                <div class="card-body p-4">
                    <h4 class="mb-4">Contact Us</h4>
                    <form>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Name</label>
                                <input type="text" class="form-control" name="name" placeholder="Your name">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" name="email" placeholder="your@email.com">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Message</label>
                            <textarea class="form-control" name="message" rows="4" placeholder="How can we help?"></textarea>
                        </div>
                        <button type="submit" class="btn btn-amazon">Submit</button>
                    </form>
                </div>
            </div>
            
            <div class="mt-4 text-muted">
                <small><i class="bi bi-file-earmark-text"></i> Viewing file: {{ filename }}</small>
            </div>
        </div>
    </div>
</div>
'''), filename=filename)

# 4. Command Injection - /run-diagnostic?input=
@app.route('/run-diagnostic')
def run_diagnostic():
    user_input = request.args.get('input', '')
    
    # Check for command injection patterns
    if 'cat /etc/passwd' in user_input or 'type C:\\Windows\\System32\\drivers\\etc\\hosts' in user_input:
        if ';' in user_input or '|' in user_input or '`' in user_input:
            return "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin", 200
    
    if 'sleep 5' in user_input or 'ping -n 5' in user_input:
        if ';' in user_input or '|' in user_input or '`' in user_input:
            time.sleep(5)
            return "Diagnostic completed after delay", 200
    
    # VULNERABLE: Direct command execution
    try:
        result = subprocess.check_output(user_input, shell=True, stderr=subprocess.STDOUT, timeout=10)
        return f"<pre>Diagnostic Result:\n{result.decode()}</pre>", 200
    except:
        return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-terminal"></i> System Diagnostic</h2>
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <p class="text-muted mb-4">Run system diagnostics to check server health.</p>
            
            <div class="card">
                <div class="card-body p-4">
                    <form method="get">
                        <div class="mb-3">
                            <label class="form-label">Diagnostic Command</label>
                            <input type="text" class="form-control" name="input" placeholder="e.g., ping google.com">
                        </div>
                        <button type="submit" class="btn btn-amazon w-100">Run Diagnostic</button>
                    </form>
                </div>
            </div>
            
            <div class="alert alert-info mt-4">
                <strong><i class="bi bi-info-circle"></i> Available commands:</strong> ping, nslookup, traceroute
            </div>
        </div>
    </div>
</div>
'''))

# 5. SSRF - /track-order?url=
@app.route('/track-order')
def track_order():
    url = request.args.get('url', '')
    
    # VULNERABLE: SSRF simulation
    if '169.254.169.254' in url:
        return """{
  "ami-id": "ami-12345678",
  "instance-id": "i-abcdef1234567890",
  "instance-type": "t2.micro",
  "local-ipv4": "172.31.16.139"
}""", 200
    
    if '127.0.0.1:22' in url or 'localhost:22' in url:
        return "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5", 200
    
    if url:
        return f"<h3>Tracking Order</h3><p>Fetching data from: {url}</p><p>Status: In Transit</p>", 200
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-truck"></i> Track Your Order</h2>
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <p class="text-muted mb-4">Enter your order tracking URL to get real-time updates.</p>
            
            <div class="card">
                <div class="card-body p-4">
                    <form method="get">
                        <div class="mb-3">
                            <label class="form-label">Tracking URL</label>
                            <input type="text" class="form-control" name="url" placeholder="https://...">
                        </div>
                        <button type="submit" class="btn btn-amazon w-100">Track Order</button>
                    </form>
                </div>
            </div>
            
            <div class="mt-4 text-center">
                <p class="text-muted"><i class="bi bi-question-circle"></i> Need help? <a href="/support">Contact Support</a></p>
            </div>
        </div>
    </div>
</div>
'''))

# Cart functionality - Session based cart counter
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    # Increment cart counter in session
    current_count = session.get('cart_count', 0)
    session['cart_count'] = current_count + 1
    return redirect(url_for('checkout'))

# 6. SSTI - /template?name=
@app.route('/template')
def template():
    name = request.args.get('name', 'Guest')
    
    # VULNERABLE: Server-Side Template Injection
    # Direct template rendering with user input
    template_str = get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card" style="border-top: 4px solid var(--primary-color);">
                <div class="card-body text-center p-5">
                    <i class="bi bi-shop-window" style="font-size: 3rem; color: var(--primary-color);"></i>
                    <h2 class="mt-3 mb-2">Welcome, ''' + name + '''!</h2>
                    <p class="text-muted">Thank you for visiting VulnShop. We hope you find everything you need.</p>
                    <hr class="my-4">
                    <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                        <a href="/" class="btn btn-amazon">Start Shopping</a>
                        <a href="/search" class="btn btn-outline-primary">Browse Products</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
''')
    try:
        result = render_template_string(template_str)
        return result
    except Exception as e:
        return str(e), 500

# 7. XXE - /api/xml-import (POST)
@app.route('/api/xml-import', methods=['POST'])
def xml_import():
    xml_data = request.data.decode('utf-8')
    
    # VULNERABLE: XXE - processing XML with external entities
    if '<!DOCTYPE' in xml_data and 'SYSTEM' in xml_data:
        if 'file:///etc/passwd' in xml_data:
            return "root:x:0:0:root:/root:/bin/bash\nbin:x:1:1:bin:/bin:/sbin/nologin\nImported successfully", 200
    
    try:
        # VULNERABLE: Using minidom which processes external entities by default
        doc = minidom.parseString(xml_data)
        root = doc.documentElement
        return f"XML imported successfully. Root element: {root.tagName}", 200
    except Exception as e:
        return f"Error parsing XML: {str(e)}", 400

# 8. JWT None Algorithm - /jwt-login and /jwt-protected
@app.route('/jwt-login')
def jwt_login():
    # VULNERABLE: Create token with alg: HS256 but accept none
    token = jwt.encode({'user': 'admin', 'role': 'admin'}, 'secret_key', algorithm='HS256')
    return jsonify({'token': token, 'message': 'Login successful'})

@app.route('/jwt-protected')
def jwt_protected():
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header:
        return jsonify({'error': 'Missing token'}), 403
    
    try:
        token = auth_header.replace('Bearer ', '')
        
        # VULNERABLE: Check for "none" algorithm without verification
        header_data = jwt.get_unverified_header(token)
        if header_data.get('alg') == 'none':
            # Accept token without signature verification
            payload = jwt.decode(token, options={"verify_signature": False}, algorithms=['none', 'HS256'])
            return jsonify({'message': 'Access granted', 'user': payload.get('user')}), 200
        
        # Normal verification
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        return jsonify({'message': 'Access granted', 'user': payload.get('user')}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 403

# 9. CSRF - /checkout
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # VULNERABLE: Not validating CSRF token
        name = request.form.get('name', '')
        card = request.form.get('card', '')
        csrf_token = request.form.get('csrfmiddlewaretoken', '')
        # Token accepted without validation
        return "Order placed successfully! Thank you for your purchase."[:100], 200
    
    # GET: Return form with CSRF token
    csrf_token = "dummy_csrf_token_12345"
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-credit-card"></i> Checkout</h2>
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-body p-4">
                    <h4 class="mb-4">Enter Payment Details</h4>
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="''' + csrf_token + '''">
                        <div class="mb-3">
                            <label class="form-label">Full Name</label>
                            <input type="text" class="form-control" name="name" placeholder="John Doe" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Card Number</label>
                            <input type="text" class="form-control" name="card" placeholder="1234-5678-9012-3456" required>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Expiry Date</label>
                                <input type="text" class="form-control" name="expiry" placeholder="MM/YY">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">CVV</label>
                                <input type="text" class="form-control" name="cvv" placeholder="123">
                            </div>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-amazon btn-lg">Place Order</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="mt-4 text-center">
                <p class="text-muted small"><i class="bi bi-shield-lock"></i> Secure payment processing</p>
            </div>
        </div>
    </div>
</div>
'''))

# 10. Unrestricted File Upload - /upload-review
@app.route('/upload-review', methods=['GET', 'POST'])
def upload_review():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file provided", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        
        # VULNERABLE: No extension validation - accepts any file type
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check if file contains PHP code
        with open(filepath, 'rb') as f:
            content = f.read()
            if b'<?php echo "VulnScout_Upload_Test"' in content or b'<?php' in content:
                return f"File uploaded successfully: {filename}", 200
        
        return f"File uploaded: {filename}", 200
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-upload"></i> Upload Product Review</h2>
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <p class="text-muted mb-4">Share your experience! Upload photos or documents with your review.</p>
            
            <div class="card">
                <div class="card-body p-4">
                    <form method="post" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label class="form-label">Review Text</label>
                            <textarea class="form-control" name="review" rows="3" placeholder="Write your review..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Attachment (Image, PDF, or Document)</label>
                            <input type="file" class="form-control" name="file">
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-amazon">Submit Review</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="alert alert-secondary mt-3">
                <small><i class="bi bi-info-circle"></i> Supported formats: .jpg, .png, .pdf, .php, .jsp, .asp, .aspx</small>
            </div>
        </div>
    </div>
</div>
'''))

# 11. Race Condition - /buy-ticket
# Global ticket counter (no locking)
tickets_remaining = 10

@app.route('/buy-ticket', methods=['POST'])
def buy_ticket():
    global tickets_remaining
    
    # VULNERABLE: No mutex/lock - race condition possible
    if tickets_remaining > 0:
        # Simulate some processing time
        time.sleep(0.1)
        tickets_remaining -= 1
        return jsonify({'status': 'success', 'message': 'Ticket purchased!', 'remaining': tickets_remaining}), 200
    else:
        return jsonify({'status': 'failed', 'message': 'Sold out!'}), 200

# 12. Missing Security Headers + CORS - /api/products
@app.route('/api/products')
def api_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    products_list = [dict(row) for row in products]
    
    response = make_response(jsonify(products_list))
    
    # VULNERABLE: Permissive CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['X-Powered-By'] = 'PHP/7.4.0'
    
    # VULNERABLE: Missing security headers
    # No Strict-Transport-Security
    # No Content-Security-Policy
    # No X-Frame-Options
    # No X-Content-Type-Options
    # No X-XSS-Protection
    # No Referrer-Policy
    # No Permissions-Policy
    
    return response

# 13. Directory Listing - /files/
@app.route('/files/')
def files_listing():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    
    # VULNERABLE: Directory listing enabled
    html = """<!DOCTYPE html>
<html>
<head><title>Index of /files/</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; }
h1 { border-bottom: 1px solid #ccc; padding-bottom: 10px; }
table { width: 100%%; border-collapse: collapse; }
th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
th { background-color: #f2f2f2; }
</style>
</head>
<body>
<h1>Index of /</h1>
<table>
<tr><th>Name</th><th>Size</th><th>Modified</th></tr>
"""
    
    for filename in files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        size = os.path.getsize(filepath)
        mtime = time.ctime(os.path.getmtime(filepath))
        html += f"<tr><td><a href='/files/{filename}'>{filename}</a></td><td>{size} bytes</td><td>{mtime}</td></tr>\n"
    
    html += "</table><hr><p>ShopZone File Manager</p></body></html>"
    return html

# Serve files from upload directory
@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 14. Dangerous HTTP Methods - /api/options
@app.route('/api/options', methods=['OPTIONS'])
def api_options():
    response = make_response()
    # VULNERABLE: Allowing dangerous HTTP methods
    response.headers['Allow'] = 'GET, POST, PUT, DELETE, TRACE'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, TRACE'
    return response

# 15. Admin Panel Exposed - /admin
@app.route('/admin')
def admin_panel():
    # VULNERABLE: No authentication check
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    
    # Calculate revenue dynamically from orders
    revenue_query = '''
        SELECT SUM(p.price * o.quantity) as total_revenue 
        FROM orders o 
        JOIN products p ON o.product_id = p.id
    '''
    revenue_result = conn.execute(revenue_query).fetchone()
    total_revenue = revenue_result['total_revenue'] or 0
    
    conn.close()
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="section-title mb-0"><i class="bi bi-shield-lock"></i> Admin Dashboard</h2>
        <span class="badge bg-danger">Admin Access</span>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-4">
            <div class="card bg-primary text-white h-100">
                <div class="card-body text-center p-4">
                    <h4>Total Users</h4>
                    <h2 class="mb-0">{{ users|length }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-success text-white h-100">
                <div class="card-body text-center p-4">
                    <h4>Total Orders</h4>
                    <h2 class="mb-0">{{ orders|length }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-info text-white h-100">
                <div class="card-body text-center p-4">
                    <h4>Revenue</h4>
                    <h2 class="mb-0">${{ "{:,.2f}".format(total_revenue) }}</h2>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header bg-dark text-white">
            <h5 class="mb-0"><i class="bi bi-people"></i> Registered Users</h5>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr><th>ID</th><th>Username</th><th>Email</th><th>Password</th></tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr><td>{{ user.id }}</td><td>{{ user.username }}</td><td>{{ user.email }}</td><td><code>{{ user.password }}</code></td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-header bg-dark text-white">
            <h5 class="mb-0"><i class="bi bi-gear"></i> System Logs</h5>
        </div>
        <div class="card-body">
            <pre class="mb-0">System operational. No errors detected.
Last login: admin from 192.168.1.100
Database: Connected
Uptime: 14 days, 3 hours</pre>
        </div>
    </div>
</div>
'''), users=users, orders=orders, total_revenue=total_revenue)

# 16. /manager - Return HTTP 200 with styling
@app.route('/manager')
def manager():
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <div class="d-flex justify-content-between align-items-center mb-4" style="background: var(--amazon-dark); padding: 20px; border-radius: 8px; color: white;">
        <h2 class="mb-0"><i class="bi bi-briefcase-fill"></i> Manager Console</h2>
        <span class="badge bg-warning text-dark">Management Access</span>
    </div>
    
    <div class="row g-4">
        <div class="col-md-3">
            <div class="card h-100" style="background: var(--amazon-light);">
                <div class="card-body p-0">
                    <div class="list-group list-group-flush">
                        <a href="/admin" class="list-group-item list-group-item-action" style="background: transparent; color: white; border-color: #37475a;">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a>
                        <a href="/admin" class="list-group-item list-group-item-action" style="background: transparent; color: white; border-color: #37475a;">
                            <i class="bi bi-people"></i> Users
                        </a>
                        <a href="/admin" class="list-group-item list-group-item-action" style="background: transparent; color: white; border-color: #37475a;">
                            <i class="bi bi-gear"></i> System Tools
                        </a>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-9">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="bi bi-hdd-network"></i> System Status</h5>
                </div>
                <div class="card-body">
                    <table class="table table-hover">
                        <thead>
                            <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><i class="bi bi-cpu"></i> CPU Usage</td>
                                <td>23%</td>
                                <td><span class="badge bg-success">Normal</span></td>
                            </tr>
                            <tr>
                                <td><i class="bi bi-memory"></i> Memory Usage</td>
                                <td>61%</td>
                                <td><span class="badge bg-warning">Moderate</span></td>
                            </tr>
                            <tr>
                                <td><i class="bi bi-clock"></i> Uptime</td>
                                <td>14 days</td>
                                <td><span class="badge bg-success">Stable</span></td>
                            </tr>
                            <tr>
                                <td><i class="bi bi-hdd"></i> Disk Space</td>
                                <td>45% used</td>
                                <td><span class="badge bg-success">Healthy</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
''')), 200

# 17. /administrator - Return HTTP 200 with styling
@app.route('/administrator')
def administrator():
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <div class="d-flex justify-content-between align-items-center mb-4" style="background: var(--amazon-dark); padding: 20px; border-radius: 8px; color: white;">
        <h2 class="mb-0"><i class="bi bi-shield-shaded"></i> Administrator Panel</h2>
        <span class="badge bg-danger">Administrator Access</span>
    </div>
    
    <div class="row g-4">
        <div class="col-md-4">
            <div class="card h-100" style="background: var(--amazon-light); color: white;">
                <div class="card-body">
                    <h5 class="mb-3"><i class="bi bi-link-45deg"></i> Quick Links</h5>
                    <div class="list-group list-group-flush">
                        <a href="/admin" class="list-group-item list-group-item-action" style="background: transparent; color: white; border-color: #37475a;">
                            <i class="bi bi-shield-lock"></i> Admin Dashboard
                        </a>
                        <a href="/manager" class="list-group-item list-group-item-action" style="background: transparent; color: white; border-color: #37475a;">
                            <i class="bi bi-briefcase"></i> Manager Console
                        </a>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-8">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="bi bi-sliders"></i> Advanced Configuration</h5>
                </div>
                <div class="card-body">
                    <table class="table table-sm">
                        <thead>
                            <tr><th>Setting</th><th>Value</th><th>Description</th></tr>
                        </thead>
                        <tbody>
                            <tr><td><code>debug_mode</code></td><td><span class="badge bg-success">true</span></td><td>Application debug mode</td></tr>
                            <tr><td><code>session_timeout</code></td><td>3600s</td><td>User session expiration</td></tr>
                            <tr><td><code>max_upload_size</code></td><td>100MB</td><td>File upload limit</td></tr>
                            <tr><td><code>db_encryption</code></td><td><span class="badge bg-danger">disabled</span></td><td>Database encryption status</td></tr>
                            <tr><td><code>api_rate_limit</code></td><td><span class="badge bg-danger">none</span></td><td>API request throttling</td></tr>
                            <tr><td><code>audit_logging</code></td><td><span class="badge bg-warning">partial</span></td><td>Security audit trail</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
''')), 200

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        # VULNERABLE: SQL Injection possible here too
        query = f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{password}')"
        try:
            conn.execute(query)
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            conn.close()
            return "Registration failed", 400
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <div class="row">
        <div class="col-md-4 offset-md-4">
            <div class="card">
                <div class="card-body p-4">
                    <div class="text-center mb-4">
                        <i class="bi bi-person-plus" style="font-size: 3rem; color: var(--primary-color);"></i>
                        <h3 class="mt-3">Create Account</h3>
                        <p class="text-muted">Join VulnShop today</p>
                    </div>
                    <form method="post">
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" name="username" placeholder="Choose a username" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" placeholder="your@email.com" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" placeholder="Create a password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-amazon btn-lg">Create Account</button>
                        </div>
                    </form>
                    <hr class="my-4">
                    <p class="text-center text-muted mb-0">Already have an account? <a href="/login" style="color: var(--primary-color);">Sign In</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
'''))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        # VULNERABLE: SQL Injection in login
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = conn.execute(query).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <div class="row">
        <div class="col-md-4 offset-md-4">
            <div class="card">
                <div class="card-body p-4">
                    <div class="text-center mb-4">
                        <i class="bi bi-box-arrow-in-right" style="font-size: 3rem; color: var(--primary-color);"></i>
                        <h3 class="mt-3">Sign In</h3>
                        <p class="text-muted">Welcome back to VulnShop</p>
                    </div>
                    <form method="post">
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" name="username" placeholder="Enter your username" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" placeholder="Enter your password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-amazon btn-lg">Sign In</button>
                        </div>
                    </form>
                    <hr class="my-4">
                    <p class="text-center text-muted mb-0">New to VulnShop? <a href="/register" style="color: var(--primary-color);">Create an account</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
'''))

@app.route('/dashboard')
def dashboard():
    # VULNERABLE: Weak session check - accessible without proper session
    user_id = session.get('user_id', 1)  # Defaults to user 1 if not logged in
    username = session.get('username', 'Guest')
    
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    return render_template_string(get_base_template().replace('{{ content|safe }}', '''
<div class="category-section">
    <h2 class="section-title"><i class="bi bi-person"></i> My Account</h2>
    <div class="row g-4">
        <div class="col-md-3">
            <div class="card h-100">
                <div class="card-body text-center p-4">
                    <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                        <i class="bi bi-person" style="font-size: 2.5rem;"></i>
                    </div>
                    <h4 class="mb-1">{{ username }}</h4>
                    <p class="text-muted mb-3">Member since 2024</p>
                    {% if user_id == 1 %}
                    <span class="badge bg-primary">Prime Member</span>
                    {% else %}
                    <span class="badge bg-secondary">Standard Member</span>
                    {% endif %}
                </div>
            </div>
        </div>
        <div class="col-md-9">
            <div class="card h-100">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="bi bi-bag"></i> My Orders</h5>
                </div>
                <div class="card-body">
                    {% if orders %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr><th>Order ID</th><th>Product</th><th>Quantity</th><th>Status</th><th>Action</th></tr>
                            </thead>
                            <tbody>
                                {% for order in orders %}
                                <tr>
                                    <td>#{{ order.id }}</td>
                                    <td>Product #{{ order.product_id }}</td>
                                    <td>{{ order.quantity }}</td>
                                    <td><span class="badge bg-info">{{ order.status }}</span></td>
                                    <td><a href="/track-order" class="btn btn-sm btn-outline-primary">Track</a></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-5">
                        <i class="bi bi-bag-x" style="font-size: 3rem; color: #ccc;"></i>
                        <p class="text-muted mt-3">No orders yet. <a href="/">Start shopping!</a></p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <div class="row g-4 mt-2">
        <div class="col-md-4">
            <a href="/track-order" class="card text-decoration-none h-100">
                <div class="card-body text-center p-4">
                    <i class="bi bi-truck" style="font-size: 2rem; color: var(--primary-color);"></i>
                    <h5 class="mt-2">Your Orders</h5>
                    <p class="text-muted small mb-0">Track packages, edit or cancel orders</p>
                </div>
            </a>
        </div>
        <div class="col-md-4">
            <a href="/support" class="card text-decoration-none h-100">
                <div class="card-body text-center p-4">
                    <i class="bi bi-shield-check" style="font-size: 2rem; color: var(--primary-color);"></i>
                    <h5 class="mt-2">Login & Security</h5>
                    <p class="text-muted small mb-0">Edit login, name, and mobile number</p>
                </div>
            </a>
        </div>
        <div class="col-md-4">
            <a href="/support" class="card text-decoration-none h-100">
                <div class="card-body text-center p-4">
                    <i class="bi bi-geo-alt" style="font-size: 2rem; color: var(--primary-color);"></i>
                    <h5 class="mt-2">Your Addresses</h5>
                    <p class="text-muted small mb-0">Edit addresses for orders</p>
                </div>
            </a>
        </div>
    </div>
</div>
'''), username=username, orders=orders, user_id=user_id)

# 18. A06:2021 - Vulnerable and Outdated Components - /api/info
@app.route('/api/info')
def api_info():
    # VULNERABLE: Exposes detailed version information for reconnaissance
    return jsonify({
        'application': 'VulnShop',
        'version': '1.0.0',
        'framework': 'Flask 2.0.1',
        'python_version': '3.8.0',
        'dependencies': {
            'jinja2': '2.11.3',
            'werkzeug': '1.0.1',
            'pyyaml': '5.1',
            'jwt': '1.7.1'
        },
        'server': 'Apache/2.4.41 (Ubuntu)',
        'database': 'SQLite 3.31.1',
        'os': 'Linux 5.4.0-42-generic'
    })

# 19. A08:2021 - Software and Data Integrity Failures - /api/process
@app.route('/api/process', methods=['POST'])
def api_process():
    # VULNERABLE: Insecure deserialization without integrity verification
    data = request.form.get('data', '')
    
    try:
        # Decode base64 and unpickle - executes arbitrary code
        decoded = base64.b64decode(data)
        result = pickle.loads(decoded)  # RCE vulnerability
        return jsonify({'status': 'success', 'result': str(result)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 20. A09:2021 - Security Logging and Monitoring Failures - /api/login-audit
@app.route('/api/login-audit', methods=['POST'])
def login_audit():
    # VULNERABLE: No security logging for failed login attempts
    # No rate limiting, no account lockout, no audit trail
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    conn = None
    try:
        conn = get_db_connection()
        # Vulnerable SQL injection also present here
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = conn.execute(query).fetchone()
        
        if user:
            # No audit log of successful login
            return jsonify({'status': 'success', 'message': 'Login successful'}), 200
        else:
            # No audit log of failed login - attacker can brute force undetected
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# OWASP API Security Top 10 (2023) - Phase 1 Implementation
# ============================================================================

# API1:2023 - Broken Object Level Authorization (BOLA/IDOR)
@app.route('/api/v1/orders/<int:order_id>')
def api_get_order(order_id):
    # VULNERABLE: No authorization check - can access any order by ID
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    
    if order:
        return jsonify({
            'id': order['id'],
            'user_id': order['user_id'],
            'product_id': order['product_id'],
            'quantity': order['quantity'],
            'status': order['status'],
            'total': order['quantity'] * 99.99  # Mock price calculation
        })
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/v1/users/<int:user_id>/profile')
def api_get_user_profile(user_id):
    # VULNERABLE: No authorization - can view any user's profile
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password_hint': 'Starts with "a" and ends with "3"'  # Information disclosure
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/v1/users/<int:user_id>/addresses')
def api_get_user_addresses(user_id):
    # VULNERABLE: IDOR - returns addresses for any user
    return jsonify({
        'user_id': user_id,
        'addresses': [
            {'id': 1, 'street': '123 Test St', 'city': 'Test City', 'zip': '12345'},
            {'id': 2, 'street': '456 Hidden Ave', 'city': 'Secret City', 'zip': '67890'}
        ]
    })

# API2:2023 - Broken Authentication
@app.route('/api/v1/auth/refresh', methods=['POST'])
def api_auth_refresh():
    # VULNERABLE: Refresh token never expires, no rotation
    refresh_token = request.json.get('refresh_token', '')
    
    # Decode without checking expiration
    try:
        payload = jwt.decode(refresh_token, 'secret_key', options={"verify_exp": False}, algorithms=['HS256'])
        # Issue new access token
        new_token = jwt.encode({'user': payload.get('user'), 'role': payload.get('role')}, 'secret_key', algorithm='HS256')
        return jsonify({'access_token': new_token})
    except:
        return jsonify({'error': 'Invalid refresh token'}), 401

@app.route('/api/v1/auth/password-reset', methods=['POST'])
def api_password_reset():
    # VULNERABLE: No rate limiting, predictable reset tokens
    email = request.json.get('email', '')
    
    # Generate predictable token based on email and timestamp
    import hashlib
    import time
    timestamp = int(time.time()) // 3600  # Changes every hour
    reset_token = hashlib.md5(f"{email}{timestamp}reset".encode()).hexdigest()
    
    return jsonify({
        'message': 'Password reset email sent',
        'debug_token': reset_token,  # Information disclosure for testing
        'token_pattern': 'MD5(email + current_hour + "reset")'
    })

# API3:2023 - Broken Object Property Level Authorization (Mass Assignment)
@app.route('/api/v1/users/me', methods=['POST', 'PUT'])
def api_update_user_me():
    # VULNERABLE: Mass assignment - accepts any fields from request
    data = request.get_json()
    user_id = session.get('user_id', 1)
    
    conn = None
    try:
        conn = get_db_connection()
        
        # Build dynamic update query - accepts ANY fields
        set_clauses = []
        values = []
        for key, value in data.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        if set_clauses:
            # VULNERABLE: SQL injection also possible here
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
            values.append(user_id)
            
            conn.execute(query, values)
            conn.commit()
            
            # Return updated user - may expose hidden fields
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            
            return jsonify({
                'message': 'User updated',
                'user': dict(user)  # May expose password, role, api_keys
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        if conn:
            conn.close()
    
    return jsonify({'error': 'No data provided'}), 400

# API4:2023 - Unrestricted Resource Consumption
@app.route('/api/v1/products/export')
def api_export_products():
    # VULNERABLE: No pagination limit, can export entire database
    limit = request.args.get('limit', 1000000)  # Default 1M records
    
    conn = get_db_connection()
    # VULNERABLE: No maximum limit check
    products = conn.execute(f'SELECT * FROM products LIMIT {limit}').fetchall()
    conn.close()
    
    products_list = [dict(row) for row in products]
    
    # Simulate heavy processing
    import time
    time.sleep(0.001 * len(products_list))  # 1ms per record
    
    return jsonify({
        'count': len(products_list),
        'products': products_list
    })

@app.route('/api/v1/search')
def api_search_heavy():
    # VULNERABLE: Heavy regex search without limits
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    # VULNERABLE: Regex search without timeout
    search_query = f"SELECT * FROM products WHERE name REGEXP '{query}' OR description REGEXP '{query}'"
    
    try:
        products = conn.execute(search_query).fetchall()
        conn.close()
        return jsonify({'count': len(products), 'products': [dict(row) for row in products]})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# API5:2023 - Broken Function Level Authorization
@app.route('/api/v1/admin/users')
def api_admin_users():
    # VULNERABLE: Only checks if user has ANY JWT, not admin role
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Only checks signature, not role
        token = auth_header.replace('Bearer ', '')
        jwt.decode(token, 'secret_key', algorithms=['HS256'])
        
        # Returns all users with passwords
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        
        return jsonify({'users': [dict(row) for row in users]})
    except:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/v1/admin/orders/delete/<int:order_id>', methods=['POST', 'DELETE'])
def api_admin_delete_order(order_id):
    # VULNERABLE: URL manipulation - only checks token, not admin role
    auth_header = request.headers.get('Authorization', '')
    
    if auth_header:
        try:
            token = auth_header.replace('Bearer ', '')
            # No role verification
            jwt.decode(token, 'secret_key', algorithms=['HS256'])
            
            conn = get_db_connection()
            conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            conn.close()
            
            return jsonify({'message': f'Order {order_id} deleted'})
        except:
            pass
    
    return jsonify({'error': 'Unauthorized'}), 401

# API6:2023 - Unrestricted Access to Sensitive Business Flows
@app.route('/api/v1/cart/apply-coupon', methods=['POST'])
def api_apply_coupon():
    # VULNERABLE: No coupon usage limits, can reuse unlimited times
    coupon_code = request.json.get('coupon_code', '')
    
    # Simple coupon logic with no tracking
    if coupon_code == 'DISCOUNT50':
        return jsonify({
            'success': True,
            'discount': 0.50,
            'message': '50% discount applied',
            'times_used': 'unlimited'  # Vulnerable: no usage tracking
        })
    
    return jsonify({'success': False, 'message': 'Invalid coupon'}), 400

@app.route('/api/v1/products/bulk-purchase', methods=['POST'])
def api_bulk_purchase():
    # VULNERABLE: No purchase quantity limits
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    # No validation on maximum quantity
    return jsonify({
        'order_id': 12345,
        'product_id': product_id,
        'quantity': quantity,
        'total': quantity * 99.99,
        'status': 'confirmed'
    })

@app.route('/api/v1/reviews/rate', methods=['POST'])
def api_rate_product():
    # VULNERABLE: No rate limiting - can spam reviews
    product_id = request.json.get('product_id')
    rating = request.json.get('rating')
    review = request.json.get('review', '')
    
    return jsonify({
        'review_id': 9999,
        'product_id': product_id,
        'rating': rating,
        'review': review,
        'status': 'posted'
    })

# API7:2023 - Server Side Request Forgery (Additional variant)
@app.route('/api/v1/products/import', methods=['POST'])
def api_import_products():
    # VULNERABLE: URL-based import without validation
    source_url = request.json.get('source')
    
    try:
        import urllib.request
        # VULNERABLE: No URL validation, can access internal services
        response = urllib.request.urlopen(source_url, timeout=10)
        data = response.read().decode('utf-8')
        
        return jsonify({
            'success': True,
            'source': source_url,
            'data_length': len(data),
            'sample': data[:500]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/webhooks', methods=['POST'])
def api_register_webhook():
    # VULNERABLE: No URL validation on webhook registration
    webhook_url = request.json.get('url')
    event = request.json.get('event', 'order.created')
    
    return jsonify({
        'webhook_id': 8888,
        'url': webhook_url,
        'event': event,
        'status': 'active'
    })

# API8:2023 - Security Misconfiguration
@app.route('/api/v1/debug')
def api_debug():
    # VULNERABLE: Debug endpoint exposes sensitive information
    import sys
    import os
    
    return jsonify({
        'environment': {
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
            'SECRET_KEY': app.secret_key,
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'sqlite:///shopzone.db'),
            'PWD': os.getcwd()
        },
        'system': {
            'python_version': sys.version,
            'platform': sys.platform,
            'modules': [m for m in sys.modules.keys()][:50]
        },
        'request': {
            'headers': dict(request.headers),
            'remote_addr': request.remote_addr,
            'user_agent': str(request.user_agent)
        }
    })

@app.route('/api/v1/')
def api_root():
    # VULNERABLE: Stack traces exposed in error responses
    if request.args.get('error'):
        # Intentionally trigger error
        1 / 0  # ZeroDivisionError
    
    return jsonify({
        'version': 'v1',
        'endpoints': ['/users', '/orders', '/products', '/admin'],
        'documentation': '/api/docs'  # Non-existent endpoint
    })

# API9:2023 - Improper Inventory Management
@app.route('/api/v2/')
def api_v2_deprecated():
    # VULNERABLE: Deprecated API still accessible with sensitive endpoints
    return jsonify({
        'message': 'API v2 is deprecated, use v3',
        'deprecation_date': '2023-01-01',
        'endpoints': {
            'users': '/api/v2/users (BETA)',
            'payments': '/api/v2/payments (INTERNAL USE ONLY)',
            'secrets': '/api/v2/config/secrets'
        }
    })

@app.route('/api/internal/')
def api_internal():
    # VULNERABLE: Internal API exposed externally
    return jsonify({
        'internal_api': True,
        'endpoints': [
            '/api/internal/health/detailed',
            '/api/internal/config',
            '/api/internal/logs',
            '/api/internal/database/status'
        ],
        'requires_vpn': False  # False - exposed to public
    })

@app.route('/api/beta/')
def api_beta():
    # VULNERABLE: Beta features in production with experimental endpoints
    return jsonify({
        'beta_features': [
            {'name': 'AI Recommendations', 'endpoint': '/api/beta/ai/recommend'},
            {'name': 'Payment v3', 'endpoint': '/api/beta/payments/crypto'},
            {'name': 'User Analytics', 'endpoint': '/api/beta/analytics/user-tracking'}
        ],
        'warning': 'Beta endpoints may expose sensitive data'
    })

# API10:2023 - Unsafe Consumption of APIs
@app.route('/api/v1/payment/process', methods=['POST'])
def api_payment_process():
    # VULNERABLE: Blindly forwards request to payment gateway without validation
    payment_data = request.get_json()
    
    # Simulate forwarding to external payment API
    # No validation of amount, currency, or recipient
    external_response = {
        'gateway': 'external-payment-provider',
        'status': 'processed',
        'amount': payment_data.get('amount'),
        'currency': payment_data.get('currency', 'USD'),
        'recipient': payment_data.get('recipient_account'),
        'note': 'Forwarded without validation - potential payment manipulation'
    }
    
    return jsonify(external_response)

@app.route('/api/v1/shipping/calculate', methods=['POST'])
def api_shipping_calculate():
    # VULNERABLE: No validation of external API response
    zip_code = request.json.get('zip_code', '')
    
    # Simulate external API call
    import random
    external_response = {
        'cost': random.uniform(5.0, 50.0),
        'carrier': 'external-shipping-api',
        'delivery_date': '2024-12-31',
        'internal_note': 'User agent: python-requests/2.28.0'  # Information disclosure from external API
    }
    
    # No validation - directly returns external data
    return jsonify(external_response)

# ============================================================================
# End OWASP API Security Top 10 Implementation
# ============================================================================

# ============================================================================
# Phase 2: Business Logic Vulnerabilities
# ============================================================================

# Payment Manipulation
@app.route('/api/v1/checkout/apply-discount', methods=['POST'])
def api_apply_discount():
    # VULNERABLE: Allows stacking multiple discounts
    discounts = request.json.get('discounts', [])
    base_price = request.json.get('base_price', 100.0)
    
    final_price = base_price
    applied_discounts = []
    
    # No limit on number of discounts
    for discount in discounts:
        if discount.get('type') == 'percentage':
            final_price = final_price * (1 - discount.get('value', 0))
            applied_discounts.append(discount)
        elif discount.get('type') == 'fixed':
            final_price = final_price - discount.get('value', 0)
            applied_discounts.append(discount)
    
    # Can go negative - store owes money to customer
    return jsonify({
        'base_price': base_price,
        'final_price': final_price,
        'applied_discounts': len(applied_discounts),
        'discounts_detail': applied_discounts
    })

@app.route('/api/v1/cart/update-price', methods=['POST'])
def api_update_cart_price():
    # VULNERABLE: Client-side price control
    item_id = request.json.get('item_id')
    client_price = request.json.get('price')  # No server-side validation
    
    return jsonify({
        'item_id': item_id,
        'price_set': client_price,
        'status': 'price_updated',
        'note': 'Price accepted from client without verification'
    })

@app.route('/api/v1/wallet/add-funds', methods=['POST'])
def api_add_funds():
    # VULNERABLE: Race condition on wallet balance
    amount = request.json.get('amount', 0)
    user_id = session.get('user_id', 1)
    
    # Simulate concurrent requests vulnerability
    # In real implementation, this would be:
    # balance = get_balance(user_id)
    # set_balance(user_id, balance + amount)
    # Race condition: Two concurrent requests both read same balance
    
    current_balance = session.get('wallet_balance', 0)
    new_balance = current_balance + amount
    session['wallet_balance'] = new_balance
    
    return jsonify({
        'user_id': user_id,
        'amount_added': amount,
        'new_balance': new_balance,
        'transaction_id': f'TXN{int(time.time())}'
    })

# Order Manipulation
@app.route('/api/v1/orders/modify', methods=['POST'])
def api_modify_order():
    # VULNERABLE: Can modify already shipped orders
    order_id = request.json.get('order_id')
    new_status = request.json.get('status')
    new_items = request.json.get('items', [])
    
    # No validation of current status
    # Should not allow modifications to shipped/delivered orders
    
    return jsonify({
        'order_id': order_id,
        'updated_status': new_status,
        'updated_items': new_items,
        'previous_status': 'shipped',  # Shows we modified a shipped order
        'message': 'Order modified successfully'
    })

@app.route('/api/v1/orders/cancel', methods=['POST'])
def api_cancel_order():
    # VULNERABLE: Can cancel other users' orders (IDOR + logic flaw)
    order_id = request.json.get('order_id')
    user_id = request.json.get('user_id')  # User can specify any user_id
    
    # No verification that order belongs to requesting user
    # Also no validation on cancellation window
    
    return jsonify({
        'order_id': order_id,
        'cancelled_for_user': user_id,
        'refund_amount': 999.99,
        'status': 'cancelled_and_refunded'
    })

@app.route('/api/v1/returns/process', methods=['POST'])
def api_process_return():
    # VULNERABLE: Double refund attack
    order_id = request.json.get('order_id')
    item_id = request.json.get('item_id')
    reason = request.json.get('reason', '')
    
    # No check if item was already returned
    # No check if order was already refunded
    
    refund_amount = request.json.get('refund_amount', 99.99)
    
    return jsonify({
        'return_id': f'RET{int(time.time())}',
        'order_id': order_id,
        'item_id': item_id,
        'refund_processed': refund_amount,
        'previous_returns': 'not_checked',  # Vulnerability indicator
        'status': 'refunded'
    })

# Inventory Manipulation
@app.route('/api/v1/cart/add', methods=['POST'])
def api_cart_add():
    # VULNERABLE: Negative quantity = credit to user
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    # No validation that quantity is positive
    # Negative quantity subtracts from cart total = store credit
    
    price_per_unit = 99.99
    line_total = quantity * price_per_unit  # Negative if quantity negative
    
    return jsonify({
        'product_id': product_id,
        'quantity': quantity,
        'line_total': line_total,
        'cart_updated': True,
        'note': 'Negative quantities accepted - results in store credit'
    })

@app.route('/api/v1/products/reserve', methods=['POST'])
def api_reserve_product():
    # VULNERABLE: Reserve without payment authorization
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    reservation_duration = request.json.get('duration_hours', 48)
    
    # No payment pre-authorization
    # No actual inventory decrement
    # Reservation can be extended indefinitely
    
    return jsonify({
        'reservation_id': f'RES{int(time.time())}',
        'product_id': product_id,
        'quantity_reserved': quantity,
        'expires_at': '2024-12-31T23:59:59',  # Far future
        'payment_required': False,  # Vulnerability
        'status': 'reserved'
    })

@app.route('/api/v1/wishlist/share', methods=['GET'])
def api_wishlist_share():
    # VULNERABLE: Private wishlists accessible via predictable ID
    wishlist_id = request.args.get('id', '1')
    
    # No ownership check
    # Sequential IDs allow enumeration of all wishlists
    
    return jsonify({
        'wishlist_id': wishlist_id,
        'owner': 'user_123',
        'items': [
            {'id': 1, 'name': 'Private Item 1', 'price': 299.99},
            {'id': 2, 'name': 'Private Item 2', 'price': 149.99}
        ],
        'is_public': False,  # But still accessible
        'privacy': 'private'
    })

# Time-based / Race Condition Attacks
@app.route('/api/v1/flash-sale', methods=['POST'])
def api_flash_sale():
    # VULNERABLE: Race condition on limited stock
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    # Global variable simulating stock (no locking)
    global flash_sale_stock
    flash_sale_stock = 5  # Only 5 items available
    
    # No mutex/lock - race condition possible
    if flash_sale_stock >= quantity:
        # Simulate processing time
        time.sleep(0.1)
        flash_sale_stock -= quantity
        return jsonify({
            'status': 'success',
            'message': f'Purchased {quantity} items',
            'remaining_stock': flash_sale_stock
        })
    else:
        return jsonify({
            'status': 'failed',
            'message': 'Out of stock'
        }), 400

@app.route('/api/v1/preorder', methods=['POST'])
def api_preorder():
    # VULNERABLE: Preorder without payment auth
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    customer_email = request.json.get('email')
    
    # No payment method validation
    # No charge authorization
    # Product may never ship
    
    return jsonify({
        'preorder_id': f'PRE{int(time.time())}',
        'product_id': product_id,
        'quantity': quantity,
        'email': customer_email,
        'payment_status': 'not_required',  # Vulnerability
        'charge_scheduled': 'on_shipment',
        'guaranteed_price': False
    })

@app.route('/api/v1/subscriptions/trial', methods=['POST'])
def api_subscription_trial():
    # VULNERABLE: Infinite trial loophole
    email = request.json.get('email')
    device_id = request.json.get('device_id')
    
    # Only tracks by device_id, not email or payment method
    # User can create unlimited trials with different device_ids
    
    trial_count = session.get(f'trials_{device_id}', 0)
    trial_count += 1
    session[f'trials_{device_id}'] = trial_count
    
    return jsonify({
        'trial_activated': True,
        'email': email,
        'device_id': device_id,
        'trial_number': trial_count,  # Shows unlimited trials
        'trial_duration_days': 30,
        'features': 'premium',
        'payment_required': 'after_trial'
    })

# ============================================================================
# End Phase 2: Business Logic Vulnerabilities
# ============================================================================

# ============================================================================
# Phase 3: Advanced Injection Vectors
# ============================================================================

# Mock NoSQL database (simulating MongoDB with Python dict)
nosql_db = {
    'products': [
        {'_id': 1, 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics', 'secret_note': 'Internal: Cost is $600'},
        {'_id': 2, 'name': 'Phone', 'price': 699.99, 'category': 'Electronics', 'secret_note': 'Internal: Cost is $400'},
        {'_id': 3, 'name': 'Shirt', 'price': 29.99, 'category': 'Clothing', 'secret_note': 'Internal: Cost is $10'},
    ],
    'users': [
        {'_id': 1, 'username': 'admin', 'role': 'admin', 'password': 'admin123', 'ssn': '123-45-6789'},
        {'_id': 2, 'username': 'user1', 'role': 'user', 'password': 'password123', 'ssn': '987-65-4321'},
    ]
}

# 45. NoSQL Injection (MongoDB-style)
@app.route('/api/v2/products/search', methods=['POST'])
def api_nosql_search():
    # VULNERABLE: NoSQL injection via JSON operators
    # Example attack: {"name": {"$ne": null}} - returns all products
    # Example attack: {"name": {"$regex": ".*"}} - regex DoS
    import json
    
    query = request.get_json() or {}
    
    # Vulnerable: Directly using user input as query filter
    # No sanitization of MongoDB operators ($ne, $gt, $lt, $regex, etc.)
    
    results = []
    for product in nosql_db['products']:
        match = True
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle MongoDB operators (vulnerable)
                for op, op_value in value.items():
                    if op == '$ne' and product.get(key) == op_value:
                        match = False
                    elif op == '$gt' and not (product.get(key) > op_value):
                        match = False
                    elif op == '$lt' and not (product.get(key) < op_value):
                        match = False
                    elif op == '$regex' and not re.search(op_value, str(product.get(key, ''))):
                        match = False
                    elif op == '$exists' and (product.get(key) is not None) != op_value:
                        match = False
            else:
                # Direct match
                if product.get(key) != value:
                    match = False
        
        if match:
            results.append(product)
    
    return jsonify({
        'query': query,
        'count': len(results),
        'products': results
    })

# 46. LDAP Injection
@app.route('/api/v1/auth/ldap-login', methods=['POST'])
def api_ldap_login():
    # VULNERABLE: LDAP injection in authentication
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # Vulnerable: Direct string concatenation in LDAP query
    # Example attack: username = "*)(uid=*))(&(uid=*"
    # Results in: (uid=*)(uid=*))(&(uid=*)
    
    ldap_query = f"(&(uid={username})(userPassword={password}))"
    
    # Simulate LDAP search (vulnerable logic)
    # In real LDAP injection, this would bypass auth or extract data
    
    # Check for injection patterns
    if '*))' in username or '(&' in username or '(|' in username:
        # Injection successful - bypass authentication
        return jsonify({
            'authenticated': True,
            'username': username,
            'role': 'admin',
            'ldap_query': ldap_query,
            'note': 'LDAP injection detected - authentication bypassed'
        })
    
    # Normal authentication check (also vulnerable to bypass)
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'authenticated': True,
            'username': username,
            'role': 'admin',
            'ldap_query': ldap_query
        })
    
    return jsonify({
        'authenticated': False,
        'ldap_query': ldap_query,
        'note': 'LDAP injection possible - modify query structure'
    }), 401

# 47. XPath Injection
@app.route('/api/v1/products/xml-search', methods=['POST'])
def api_xpath_search():
    # VULNERABLE: XPath injection
    from xml.etree import ElementTree as ET
    
    # Sample XML data
    xml_data = '''<?xml version="1.0"?>
    <products>
        <product id="1">
            <name>Laptop</name>
            <price>999.99</price>
            <category>Electronics</category>
        </product>
        <product id="2">
            <name>Phone</name>
            <price>699.99</price>
            <category>Electronics</category>
        </product>
        <product id="3">
            <name>Secret Product</name>
            <price>0.01</price>
            <category>Hidden</category>
        </product>
    </products>'''
    
    search_name = request.form.get('name', '')
    xpath_expr = ""
    
    # Vulnerable: Direct concatenation in XPath expression
    # Example attack: name = "' or '1'='1" - returns all products
    # Example attack: name = "']/parent::node()/*[position()=3]/*[1]" - extracts specific data
    
    try:
        root = ET.fromstring(xml_data)
        
        # Vulnerable XPath construction
        xpath_expr = f".//product[name='{search_name}']"
        
        # In real XPath injection, this would extract unauthorized data
        # Simulating vulnerable behavior
        if "'" in search_name or '"' in search_name or 'or' in search_name.lower():
            # Injection detected - return all products including hidden ones
            products = root.findall('.//product')
            return jsonify({
                'xpath_query': xpath_expr,
                'injection_detected': True,
                'products': [
                    {
                        'id': p.get('id'),
                        'name': p.findtext('name', ''),
                        'price': p.findtext('price', ''),
                        'category': p.findtext('category', '')
                    }
                    for p in products
                ],
                'note': 'XPath injection successful - all data exposed'
            })
        
        # Normal search
        products = root.findall(xpath_expr)
        
        return jsonify({
            'xpath_query': xpath_expr,
            'products': [
                {
                    'id': p.get('id'),
                    'name': p.findtext('name', ''),
                    'price': p.findtext('price', ''),
                    'category': p.findtext('category', '')
                }
                for p in products
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'xpath_query': xpath_expr}), 500

# 48. ORM Injection (SQLAlchemy-style)
@app.route('/api/v1/orders/filter', methods=['POST'])
def api_orm_filter():
    # VULNERABLE: ORM filter injection
    # Simulating SQLAlchemy ORM vulnerability
    
    filter_expr = request.json.get('filter', '')
    order_by = request.json.get('order_by', 'id')
    
    conn = get_db_connection()
    
    # VULNERABLE: Direct use of user input in ORDER BY clause
    # This is vulnerable to SQL injection even through ORM
    # Example attack: order_by = "id; DROP TABLE orders--"
    # Example attack: order_by = "id, (SELECT * FROM users)"
    
    try:
        # Vulnerable: No validation of order_by parameter
        query = f"SELECT * FROM orders ORDER BY {order_by}"
        orders = conn.execute(query).fetchall()
        conn.close()
        
        return jsonify({
            'query': query,
            'filter_applied': filter_expr,
            'order_by': order_by,
            'orders': [dict(row) for row in orders]
        })
    
    except Exception as e:
        conn.close()
        return jsonify({
            'error': str(e),
            'query': query,
            'note': 'ORM injection possible - try: order_by=id; SELECT * FROM users--'
        }), 500

# 49. Expression Language (EL) Injection
@app.route('/api/v1/template/render', methods=['POST'])
def api_template_render():
    # VULNERABLE: Expression Language injection
    # Simulating Jinja2/EL injection (similar to SSTI but for EL)
    
    template_string = request.json.get('template', '')
    context = request.json.get('context', {})
    
    # VULNERABLE: Direct rendering with user-controlled template
    # Example attacks:
    # {{ config }}
    # {{ ''.__class__.__mro__[1].__subclasses__() }}
    # ${7*7}
    # #{7*7}
    
    try:
        # Jinja2 template rendering (vulnerable)
        from jinja2 import Template
        
        # Warning: This is intentionally vulnerable
        # In production, NEVER use user input as template
        t = Template(template_string)
        result = t.render(**context)
        
        return jsonify({
            'template': template_string,
            'result': result,
            'context_keys': list(context.keys())
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'template': template_string,
            'note': 'Template injection detected - try {{7*7}} or {{config}}'
        }), 500

# 50. Command Injection via JSON Parsing
@app.route('/api/v1/parse/json', methods=['POST'])
def api_parse_json():
    # VULNERABLE: Command injection through JSON parsing
    import json
    import subprocess
    
    json_data = request.data.decode('utf-8')
    
    # VULNERABLE: Using user input in shell command
    # Example attack: json_data containing shell metacharacters
    # ; cat /etc/passwd
    # `whoami`
    # $(id)
    
    try:
        # Dangerous: Passing user input to shell
        # This is a simulated vulnerability
        if any(c in json_data for c in [';', '|', '`', '$', '&']):
            return jsonify({
                'warning': 'Command injection attempt detected',
                'received_data': json_data,
                'parsed': None,
                'note': 'Shell metacharacters found in JSON'
            })
        
        # Normal JSON parsing
        data = json.loads(json_data)
        
        return jsonify({
            'parsed': data,
            'status': 'success'
        })
    
    except json.JSONDecodeError as e:
        return jsonify({
            'error': 'Invalid JSON',
            'details': str(e),
            'received': json_data[:100]
        }), 400

# ============================================================================
# End Phase 3: Advanced Injection Vectors
# ============================================================================

# ============================================================================
# Phase 4: Cloud & Infrastructure Vulnerabilities
# ============================================================================

# Mock cloud resources
cloud_secrets = {
    'aws_access_key': 'AKIAIOSFODNN7EXAMPLE',
    'aws_secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    'azure_connection': 'DefaultEndpointsProtocol=https;AccountName=vulnshop;AccountKey=dGhpcyBpcyBhIHNlY3JldA==',
    'gcp_service_account': '{"type": "service_account", "project_id": "vulnshop", "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIB...\\n-----END PRIVATE KEY-----\\n"}',
    'db_password': 'SuperSecretDBPass123!',
    'stripe_api_key': 'sk_live_abcdefghijklmnopqrstuvwxyz',
    'jwt_secret': 'very-secret-jwt-key-12345',
    'redis_password': 'redis-secret-987',
    'elasticsearch_creds': 'elastic:changeme@localhost:9200'
}

# 51. AWS S3 Bucket Misconfiguration
@app.route('/api/v1/storage/upload', methods=['POST'])
def api_storage_upload():
    # VULNERABLE: S3 bucket enumeration and misconfiguration
    bucket_name = request.json.get('bucket', 'vulnshop-uploads')
    file_name = request.json.get('filename', 'upload.txt')
    file_content = request.json.get('content', '')
    
    # Simulating S3 upload with no ACL validation
    # Common vulnerability: Public read/write ACL
    return jsonify({
        'uploaded': True,
        'bucket': bucket_name,
        'file': file_name,
        'url': f'https://{bucket_name}.s3.amazonaws.com/{file_name}',
        'acl': 'public-read-write',  # Vulnerable: Public ACL
        'bucket_policy': {
            'Version': '2012-10-17',
            'Statement': [{
                'Effect': 'Allow',
                'Principal': '*',
                'Action': 's3:*',
                'Resource': f'arn:aws:s3:::{bucket_name}/*'
            }]
        },
        'note': 'S3 bucket is publicly accessible - listable and writable'
    })

@app.route('/api/v1/storage/list')
def api_storage_list():
    # VULNERABLE: S3 bucket listing without authentication
    bucket_name = request.args.get('bucket', 'vulnshop-uploads')
    
    return jsonify({
        'bucket': bucket_name,
        'files': [
            {'key': 'invoices/2024/january.pdf', 'size': 1024000},
            {'key': 'backups/database.sql', 'size': 52428800},
            {'key': 'secrets/config.json', 'size': 2048},
            {'key': 'customer-data/export.csv', 'size': 10485760}
        ],
        'permissions': 'public-read',
        'listable': True,
        'message': 'Bucket contents exposed without authentication'
    })

# 52. IAM Privilege Escalation
@app.route('/api/v1/admin/assume-role', methods=['POST'])
def api_assume_role():
    # VULNERABLE: No role validation, can assume any role
    role_arn = request.json.get('role_arn', '')
    session_name = request.json.get('session_name', 'vulnshop-session')
    external_id = request.json.get('external_id')  # Optional - often bypassed
    
    # Vulnerable: No validation of role_arn format or permissions
    # User can assume admin roles, cross-account roles, etc.
    
    return jsonify({
        'assumed': True,
        'role_arn': role_arn or 'arn:aws:iam::123456789012:role/AdminRole',
        'session_name': session_name,
        'external_id': external_id,
        'credentials': {
            'AccessKeyId': 'ASIA' + 'X' * 16,
            'SecretAccessKey': 'temp-secret-key',
            'SessionToken': 'temp-session-token',
            'Expiration': '2024-12-31T23:59:59Z'
        },
        'permissions': ['AdministratorAccess', 'PowerUserAccess', '*'],
        'note': 'Role assumption without MFA or proper validation'
    })

@app.route('/api/v1/iam/policies')
def api_iam_policies():
    # VULNERABLE: IAM policy enumeration
    return jsonify({
        'policies': [
            {'name': 'AdminPolicy', 'arn': 'arn:aws:iam::123456789012:policy/AdminPolicy', 'attached_users': ['admin']},
            {'name': 'S3FullAccess', 'arn': 'arn:aws:iam::123456789012:policy/S3FullAccess', 'attached_users': ['dev', 'staging']},
            {'name': 'EC2FullAccess', 'arn': 'arn:aws:iam::123456789012:policy/EC2FullAccess', 'attached_users': ['dev']},
            {'name': 'DatabaseAccess', 'arn': 'arn:aws:iam::123456789012:policy/DatabaseAccess', 'attached_users': ['app-server']}
        ],
        'roles': [
            {'name': 'LambdaExecutionRole', 'arn': 'arn:aws:iam::123456789012:role/LambdaExecutionRole'},
            {'name': 'EC2InstanceRole', 'arn': 'arn:aws:iam::123456789012:role/EC2InstanceRole'},
            {'name': 'CrossAccountRole', 'arn': 'arn:aws:iam::123456789012:role/CrossAccountRole', 'trust_policy': 'arn:aws:iam::*:root'}
        ],
        'users': [
            {'name': 'admin', 'arn': 'arn:aws:iam::123456789012:user/admin', 'mfa_enabled': False},
            {'name': 'deployer', 'arn': 'arn:aws:iam::123456789012:user/deployer', 'access_key_age': 365}
        ]
    })

# 53. Container Vulnerabilities
@app.route('/api/v1/docker/run', methods=['POST'])
def api_docker_run():
    # VULNERABLE: Docker container escape via privileged mode
    image = request.json.get('image', 'ubuntu:latest')
    command = request.json.get('command', 'sleep 3600')
    volumes = request.json.get('volumes', [])
    privileged = request.json.get('privileged', True)  # Default true - vulnerable
    
    return jsonify({
        'container_id': f'container_{int(time.time())}',
        'image': image,
        'command': command,
        'privileged': privileged,
        'security_options': [],  # No seccomp, apparmor
        'volumes': volumes or [
            {'host': '/', 'container': '/host', 'mode': 'rw'},  # Mounted root
            {'host': '/var/run/docker.sock', 'container': '/var/run/docker.sock', 'mode': 'rw'}  # Docker socket
        ],
        'capabilities': ['ALL'],  # All capabilities granted
        'user': 'root',  # Running as root
        'note': 'Container can escape and access host filesystem'
    })

@app.route('/api/v1/container/exec', methods=['POST'])
def api_container_exec():
    # VULNERABLE: Container command execution without validation
    container_id = request.json.get('container_id', '')
    command = request.json.get('command', '')
    
    # No validation of command - can execute anything
    return jsonify({
        'container_id': container_id,
        'executed': True,
        'command': command,
        'output': f'Executed: {command}',
        'user': 'root',
        'working_dir': '/host',
        'note': 'Command execution allowed without restrictions'
    })

# 54. Kubernetes Misconfigurations
@app.route('/api/v1/k8s/pods')
def api_k8s_pods():
    # VULNERABLE: Exposed Kubernetes API without auth
    return jsonify({
        'api_version': 'v1',
        'pods': [
            {
                'name': 'vulnshop-app-7d8f9b2c4-abc12',
                'namespace': 'production',
                'status': 'Running',
                'ip': '10.0.1.15',
                'service_account': 'default',  # Overprivileged SA
                'secrets_mounted': [
                    {'name': 'aws-credentials', 'path': '/etc/aws'},
                    {'name': 'db-password', 'path': '/etc/db'}
                ]
            },
            {
                'name': 'database-0',
                'namespace': 'production',
                'status': 'Running',
                'ip': '10.0.1.20',
                'service_account': 'db-admin'
            }
        ],
        'nodes': [
            {'name': 'worker-1', 'ip': '10.0.1.10', 'kubelet_port': 10250, 'auth': 'none'},  # Unauthenticated kubelet
            {'name': 'worker-2', 'ip': '10.0.1.11', 'kubelet_port': 10250, 'auth': 'none'}
        ],
        'cluster_info': {
            'kubernetes_version': 'v1.24.0',
            'etcd_endpoint': 'http://etcd:2379',  # Unencrypted etcd
            'api_server': 'https://kubernetes.default:6443'
        }
    })

@app.route('/api/v1/k8s/secrets')
def api_k8s_secrets():
    # VULNERABLE: Kubernetes secrets exposed
    return jsonify({
        'namespace': 'production',
        'secrets': [
            {'name': 'aws-credentials', 'type': 'Opaque', 'data': {'access_key': 'QUtJQUlPU0ZPRE5ON0VYQU1QTEU=', 'secret_key': 'd0phbHJYVXRuRkVNTS9LN01ERU5HL2JQeFJmaUNZRVhBTVBMS0VZ'}},
            {'name': 'db-password', 'type': 'Opaque', 'data': {'password': 'U3VwZXJTZWNyZXREQlBhc3MxMjMh'}},
            {'name': 'tls-certs', 'type': 'kubernetes.io/tls', 'data': {'tls.crt': 'LS0tLS1CRUdJTi...', 'tls.key': 'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0t'}},
            {'name': 'api-keys', 'type': 'Opaque', 'data': {'stripe': 'c2tfbGl2ZV9hYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5eg==', 'sendgrid': 'U0cueHh4eHh4eHh4eHh4eHh4eC55eHh4eHh4eC14eHh4eHh4eC14eHh4eHh4eC4='}}
        ],
        'service_accounts': [
            {'name': 'default', 'namespace': 'production', 'automount_token': True},
            {'name': 'cluster-admin', 'namespace': 'kube-system', 'automount_token': True}
        ]
    })

# 55. Secrets Management Failures
@app.route('/api/v1/secrets/get')
def api_secrets_get():
    # VULNERABLE: Secrets API with no access control
    secret_name = request.args.get('name', 'all')
    
    if secret_name == 'all':
        return jsonify(cloud_secrets)
    else:
        return jsonify({
            'secret_name': secret_name,
            'value': cloud_secrets.get(secret_name, 'Secret not found'),
            'exposure_method': 'environment_variable',  # Common mistake
            'rotation_date': '2023-01-01'  # Never rotated
        })

@app.route('/api/v1/environment')
def api_environment():
    # VULNERABLE: Exposes all environment variables
    import os
    
    env_vars = dict(os.environ)
    
    # Add some sensitive vars that might be set
    env_vars.update({
        'AWS_ACCESS_KEY_ID': cloud_secrets['aws_access_key'],
        'AWS_SECRET_ACCESS_KEY': cloud_secrets['aws_secret_key'],
        'DATABASE_URL': f'postgresql://admin:{cloud_secrets["db_password"]}@db.internal:5432/vulnshop',
        'REDIS_URL': f'redis://:{cloud_secrets["redis_password"]}@redis.internal:6379',
        'JWT_SECRET': cloud_secrets['jwt_secret'],
        'STRIPE_SECRET_KEY': cloud_secrets['stripe_api_key']
    })
    
    return jsonify({
        'environment_variables': env_vars,
        'hostname': os.uname().nodename if hasattr(os, 'uname') else 'vulnshop-prod-01',
        'cwd': os.getcwd(),
        'user': os.environ.get('USER', 'root')
    })

# 56. DevOps/CI-CD Vulnerabilities
@app.route('/api/v1/ci/build-trigger', methods=['POST'])
def api_ci_build_trigger():
    # VULNERABLE: No webhook signature validation
    repo_url = request.json.get('repo_url', '')
    branch = request.json.get('branch', 'main')
    commit = request.json.get('commit', '')
    command = request.json.get('command', '')  # Arbitrary command injection
    
    # Simulating CI pipeline trigger without validation
    return jsonify({
        'build_id': f'build_{int(time.time())}',
        'status': 'triggered',
        'repo': repo_url,
        'branch': branch,
        'commit': commit,
        'pipeline': {
            'steps': [
                'git clone',
                'pip install -r requirements.txt',
                command or 'pytest',  # Vulnerable: User can inject commands
                'docker build',
                'docker push'
            ],
            'environment': 'production',
            'privileged': True  # Dangerous: Running privileged containers
        },
        'vulnerability': 'No webhook signature validation - can trigger builds from any source'
    })

@app.route('/api/v1/deploy/status')
def api_deploy_status():
    # VULNERABLE: Deployment status reveals internal infrastructure
    return jsonify({
        'deployment_id': 'deploy-prod-2024-001',
        'status': 'active',
        'infrastructure': {
            'cloud_provider': 'AWS',
            'region': 'us-east-1',
            'vpc_id': 'vpc-0a1b2c3d4e5f6g7h8',
            'subnets': ['subnet-123', 'subnet-456'],
            'security_groups': ['sg-ssh-open-world', 'sg-http-open'],
            'load_balancer': 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/vulnshop',
            'database': {
                'host': 'vulnshop-db.cluster-abc123.us-east-1.rds.amazonaws.com',
                'port': 5432,
                'backup_enabled': False  # No backups
            }
        },
        'containers': [
            {'image': 'vulnshop:latest', 'tag': 'latest', 'digest': 'sha256:abc123'},  # Using 'latest' tag
            {'image': 'redis:alpine', 'tag': 'alpine', 'privileged': True}
        ],
        'git_info': {
            'commit': 'abc123def456',
            'branch': 'main',
            'author': 'deploy@vulnshop.com',
            'message': 'Deployed with hardcoded credentials'
        }
    })

@app.route('/api/v1/git/repo')
def api_git_repo():
    # VULNERABLE: Exposes git repository information
    return jsonify({
        'repository': 'https://github.com/vulnshop/vulnshop-prod',
        'branches': ['main', 'develop', 'feature/new-feature', 'hotfix/security-patch'],
        'commits': [
            {'hash': 'abc123', 'message': 'Added AWS keys to config', 'author': 'dev1@vulnshop.com'},
            {'hash': 'def456', 'message': 'Disable auth for testing', 'author': 'dev2@vulnshop.com'},
            {'hash': 'ghi789', 'message': 'WIP: Admin backdoor', 'author': 'attacker@evil.com'}  # Suspicious
        ],
        'files': [
            '.env',  # Should not be in repo
            'config/production.yml',
            'secrets/keys.json',  # Should not be in repo
            'docker-compose.yml',
            '.aws/credentials'  # Should not be in repo
        ],
        'ci_config': {
            'github_actions': '.github/workflows/deploy.yml',
            'gitlab_ci': '.gitlab-ci.yml',
            'jenkins': 'Jenkinsfile'
        }
    })

# ============================================================================
# End Phase 4: Cloud & Infrastructure Vulnerabilities
# ============================================================================

# ============================================================================
# Phase 5: GraphQL, Mobile, and WebSocket Vulnerabilities
# ============================================================================

# Mock GraphQL data store
graphql_users = [
    {'id': '1', 'username': 'admin', 'email': 'admin@vulnshop.com', 'password': 'admin123', 'ssn': '123-45-6789', 'role': 'admin', 'salary': 150000},
    {'id': '2', 'username': 'user1', 'email': 'user1@vulnshop.com', 'password': 'password123', 'ssn': '987-65-4321', 'role': 'user', 'salary': 50000},
    {'id': '3', 'username': 'user2', 'email': 'user2@vulnshop.com', 'password': 'password456', 'ssn': '456-78-9012', 'role': 'user', 'salary': 60000},
]

graphql_orders = [
    {'id': '1', 'user_id': '1', 'total': 999.99, 'items': ['Laptop', 'Mouse'], 'status': 'delivered', 'address': '123 Admin St'},
    {'id': '2', 'user_id': '2', 'total': 199.99, 'items': ['Phone Case', 'Charger'], 'status': 'shipped', 'address': '456 User Ave'},
    {'id': '3', 'user_id': '1', 'total': 2999.99, 'items': ['Server', 'Monitor', 'Keyboard'], 'status': 'processing', 'address': '123 Admin St'},
]

# 64. GraphQL Introspection Enabled
@app.route('/graphql', methods=['POST', 'GET'])
def graphql_endpoint():
    # VULNERABLE: Introspection enabled, no query depth limiting
    if request.method == 'GET':
        query = request.args.get('query', '')
    else:
        query = request.json.get('query', '') if request.json else ''
    
    # VULNERABLE: Introspection query allowed
    if 'IntrospectionQuery' in query or '__schema' in query or '__type' in query:
        return jsonify({
            'data': {
                '__schema': {
                    'queryType': {'name': 'Query'},
                    'mutationType': {'name': 'Mutation'},
                    'types': [
                        {'name': 'User', 'fields': [
                            {'name': 'id', 'type': 'ID'},
                            {'name': 'username', 'type': 'String'},
                            {'name': 'email', 'type': 'String'},
                            {'name': 'password', 'type': 'String'},  # Should not be exposed
                            {'name': 'ssn', 'type': 'String'},  # Sensitive field
                            {'name': 'salary', 'type': 'Int'}  # Sensitive field
                        ]},
                        {'name': 'Order', 'fields': [
                            {'name': 'id', 'type': 'ID'},
                            {'name': 'user_id', 'type': 'ID'},
                            {'name': 'total', 'type': 'Float'},
                            {'name': 'items', 'type': '[String]'},
                            {'name': 'address', 'type': 'String'}
                        ]}
                    ]
                }
            }
        })
    
    # VULNERABLE: No query depth limiting
    # Can cause DoS with deeply nested queries
    # Example: users { orders { user { orders { user { ... } } } } }
    
    # Simple query parser (vulnerable)
    if 'users' in query:
        # Check for nested queries - no depth limit
        depth = query.count('{')
        
        # Return all users with all fields - no field-level auth
        return jsonify({
            'data': {
                'users': graphql_users
            },
            'query_depth': depth,
            'warning': 'No depth limiting - nested queries can cause DoS'
        })
    
    if 'orders' in query:
        user_id = None
        # VULNERABLE: No authorization check
        # Can view any user's orders by manipulating query
        if 'userId' in query:
            # Extract user_id from query - no validation
            user_id = '1'  # Mock extraction
        
        return jsonify({
            'data': {
                'orders': graphql_orders if not user_id else [o for o in graphql_orders if o['user_id'] == user_id]
            }
        })
    
    return jsonify({
        'error': 'Invalid query',
        'note': 'GraphQL introspection enabled - query the schema to discover all types and fields'
    }), 400

# 65. GraphQL Batching Attack
@app.route('/graphql/batch', methods=['POST'])
def graphql_batch():
    # VULNERABLE: Query batching allows bypassing rate limits
    # Send 100+ queries in one request to brute force passwords
    
    queries = request.json.get('queries', [])
    
    results = []
    for i, q in enumerate(queries[:1000]):  # No limit on batch size
        results.append({
            'id': i,
            'result': f'Query {i} executed',
            'data': 'mock_result'
        })
    
    return jsonify({
        'batch_results': results,
        'queries_processed': len(queries),
        'note': 'Batching allows sending unlimited queries in one request - use for brute force'
    })

# 66. GraphQL SQL Injection via Arguments
@app.route('/graphql/search', methods=['POST'])
def graphql_search():
    # VULNERABLE: Arguments passed directly to SQL
    search_term = request.json.get('variables', {}).get('search', '')
    
    # Simulating vulnerable SQL construction
    sql = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
    
    return jsonify({
        'data': {
            'search': {
                'query': sql,
                'results': 'mock_products'
            }
        },
        'vulnerability': 'SQL injection via GraphQL variables',
        'payload_example': "{\"variables\": {\"search\": \"' OR '1'='1\"}}"
    })

# 67. Mobile API - Insecure Data Storage
@app.route('/api/v1/mobile/sync', methods=['POST'])
def api_mobile_sync():
    # VULNERABLE: Syncs sensitive data to device without encryption
    user_id = request.json.get('user_id', '1')
    device_id = request.json.get('device_id', '')
    
    return jsonify({
        'sync_id': f'sync_{int(time.time())}',
        'device': device_id,
        'data': {
            'user_profile': {
                'id': user_id,
                'username': 'user1',
                'email': 'user1@vulnshop.com',
                'password': 'plaintext_password123',  # Vulnerable: Plaintext
                'credit_card': '4532-1234-5678-9012',  # Vulnerable: Unencrypted
                'cvv': '123',  # Vulnerable: CVV stored
                'address': '123 Test St, Test City, 12345'
            },
            'order_history': [
                {'id': 1, 'total': 999.99, 'items': ['Laptop'], 'payment_method': 'visa_ending_1234'},
                {'id': 2, 'total': 49.99, 'items': ['Shirt'], 'payment_method': 'mastercard_ending_5678'}
            ],
            'session_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlcjEiLCJyb2xlIjoidXNlciJ9',  # Never expires
        },
        'encryption': 'none',  # Vulnerable: No encryption
        'storage': 'local_storage',  # Vulnerable: Local storage
        'note': 'Sensitive data stored on device without encryption'
    })

# 68. Mobile API - Insecure Communication
@app.route('/api/v1/mobile/config')
def api_mobile_config():
    # VULNERABLE: Forces HTTP instead of HTTPS
    return jsonify({
        'api_endpoints': {
            'base_url': 'http://api.vulnshop.com',  # HTTP not HTTPS
            'auth': 'http://api.vulnshop.com/auth',
            'payment': 'http://api.vulnshop.com/payment',  # Payment over HTTP!
            'upload': 'http://api.vulnshop.com/upload'
        },
        'ssl_pinning': False,  # Vulnerable: No certificate pinning
        'certificate_validation': False,  # Vulnerable: Accepts any cert
        'allowed_ciphers': ['RC4', 'DES', '3DES'],  # Vulnerable: Weak ciphers
        'min_tls_version': '1.0',  # Vulnerable: Old TLS
        'note': 'Communication vulnerable to MITM attacks'
    })

# 69. Mobile API - Hardcoded Credentials
@app.route('/api/v1/mobile/app-config')
def api_mobile_app_config():
    # VULNERABLE: Returns hardcoded credentials for mobile app
    return jsonify({
        'api_keys': {
            'aws_access_key': 'AKIAIOSFODNN7EXAMPLE',
            'aws_secret': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'firebase_api_key': 'AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'google_maps_api': 'AIzaSyAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'stripe_publishable': 'pk_live_xxxxxxxxxxxxxxxxxxxxxxxx',
            'stripe_secret': 'sk_live_xxxxxxxxxxxxxxxxxxxxxxxx'
        },
        'backend_credentials': {
            'admin_user': 'mobile_admin',
            'admin_pass': 'mobile_admin_pass_123',
            'db_host': 'db.vulnshop.internal',
            'db_user': 'mobile_app',
            'db_pass': 'mobile_db_password'
        },
        'encryption_key': 'hardcoded_aes_key_1234567890123456',  # Hardcoded key
        'note': 'Credentials hardcoded in mobile app binary'
    })

# 70. Mobile API - Root/Jailbreak Detection Bypass
@app.route('/api/v1/mobile/check-device', methods=['POST'])
def api_check_device():
    # VULNERABLE: Device integrity check is client-side only
    is_rooted = request.json.get('is_rooted', False)
    is_emulator = request.json.get('is_emulator', False)
    integrity_check = request.json.get('integrity_check_passed', True)
    
    # Server trusts client response
    return jsonify({
        'device_approved': True,  # Always approves based on client input
        'is_rooted': is_rooted,  # Server accepts client claim
        'is_emulator': is_emulator,
        'integrity_check': integrity_check,
        'security_level': 'high' if not is_rooted else 'low',
        'access_granted': True,  # Never denies access
        'note': 'Client can claim device is not rooted to bypass security'
    })

# WebSocket Vulnerabilities
connected_clients = {}
ws_message_history = []

# 71. WebSocket - No Authentication
@sock.route('/ws/chat')
def ws_chat(ws):
    # VULNERABLE: No authentication on WebSocket connection
    client_id = f'client_{int(time.time())}_{random.randint(1000, 9999)}'
    connected_clients[client_id] = ws
    
    try:
        while True:
            data = ws.receive()
            if data:
                message = json.loads(data)
                
                # VULNERABLE: No message validation
                # Can impersonate any user
                sender = message.get('username', 'anonymous')
                msg_text = message.get('message', '')
                
                # Store in history (no limit)
                ws_message_history.append({
                    'sender': sender,
                    'message': msg_text,
                    'timestamp': time.time()
                })
                
                # Broadcast to all clients
                broadcast = {
                    'type': 'message',
                    'sender': sender,
                    'message': msg_text,
                    'impersonation_possible': True,
                    'note': 'No authentication - anyone can send as any username'
                }
                
                # Send to all connected clients
                for cid, client_ws in connected_clients.items():
                    try:
                        client_ws.send(json.dumps(broadcast))
                    except:
                        pass
    except:
        pass
    finally:
        connected_clients.pop(client_id, None)

# 72. WebSocket - Message Flood / DoS
@sock.route('/ws/notifications')
def ws_notifications(ws):
    # VULNERABLE: No rate limiting on WebSocket
    client_id = f'notif_client_{int(time.time())}'
    
    try:
        while True:
            data = ws.receive()
            if data:
                # VULNERABLE: No rate limiting
                # Client can send thousands of messages
                message_count = 0
                
                # Simulate processing many messages
                for i in range(1000):  # Client could request this
                    ws.send(json.dumps({
                        'type': 'notification',
                        'count': i,
                        'data': 'x' * 10000  # Large payload
                    }))
                    message_count += 1
                
                # No rate limiting feedback
                ws.send(json.dumps({
                    'status': 'sent',
                    'messages_sent': message_count,
                    'warning': 'No rate limiting - can flood server'
                }))
    except:
        pass

# 73. WebSocket - Cross-Site WebSocket Hijacking (CSWSH)
@app.route('/api/v1/ws/config')
def api_ws_config():
    # VULNERABLE: No origin validation for WebSocket
    return jsonify({
        'websocket_endpoint': 'ws://vulnshop.com/ws/chat',
        'origin_policy': 'none',  # Vulnerable: Accepts any origin
        'allowed_origins': ['*'],  # Wildcard - vulnerable
        'csrf_protection': False,
        'session_validation': False,
        'note': 'WebSocket accepts connections from any origin - vulnerable to CSWSH'
    })

# 74. WebSocket - Information Disclosure
@app.route('/api/v1/ws/status')
def api_ws_status():
    # VULNERABLE: Exposes internal WebSocket state
    return jsonify({
        'connected_clients': len(connected_clients),
        'client_list': list(connected_clients.keys()),  # Exposes client IDs
        'message_history': ws_message_history[-100:],  # Last 100 messages
        'internal_state': {
            'server_uptime': 3600,
            'memory_usage': '1.5GB',
            'active_threads': len(connected_clients),
            'server_version': '1.0.0-vulnerable'
        }
    })

# ============================================================================
# End Phase 5: GraphQL, Mobile, and WebSocket Vulnerabilities
# ============================================================================

# ============================================================================
# Phase 6: Cryptographic Vulnerabilities
# ============================================================================

# 75. Weak Encryption Algorithm (DES/3DES)
@app.route('/api/v1/crypto/encrypt', methods=['POST'])
def api_weak_encrypt():
    # VULNERABLE: Uses DES encryption (broken algorithm)
    from Crypto.Cipher import DES
    
    data = request.json.get('data', '')
    key = request.json.get('key', 'weakkey1')  # 8 bytes for DES
    
    # Pad key to 8 bytes
    key = key[:8].ljust(8, '0')
    
    # DES is cryptographically broken
    cipher = DES.new(key.encode(), DES.MODE_ECB)
    padded_data = data + ' ' * (8 - len(data) % 8)
    encrypted = cipher.encrypt(padded_data.encode())
    
    return jsonify({
        'algorithm': 'DES',
        'mode': 'ECB',  # Also vulnerable - no IV
        'key': key,
        'encrypted': base64.b64encode(encrypted).decode(),
        'warning': 'DES is cryptographically broken - easily cracked'
    })

# 76. ECB Mode (Electronic Codebook) - No IV
@app.route('/api/v1/crypto/encrypt-aes', methods=['POST'])
def api_aes_ecb():
    # VULNERABLE: Uses AES in ECB mode
    from Crypto.Cipher import AES
    
    data = request.json.get('data', '')
    key = request.json.get('key', 'weak_aes_key_123')[:16].ljust(16, '0')
    
    # ECB mode is vulnerable to pattern analysis
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    padded_data = data + ' ' * (16 - len(data) % 16)
    encrypted = cipher.encrypt(padded_data.encode())
    
    return jsonify({
        'algorithm': 'AES-128',
        'mode': 'ECB',  # Vulnerable: identical plaintext blocks = identical ciphertext
        'key': key,
        'encrypted': base64.b64encode(encrypted).decode(),
        'warning': 'ECB mode leaks information about plaintext patterns'
    })

# 77. Static/Predictable IV
@app.route('/api/v1/crypto/encrypt-cbc', methods=['POST'])
def api_aes_static_iv():
    # VULNERABLE: Uses static IV
    from Crypto.Cipher import AES
    
    data = request.json.get('data', '')
    key = request.json.get('key', 'weak_aes_key_123')[:16].ljust(16, '0')
    
    # Static IV - major vulnerability
    static_iv = b'1234567890123456'  # Never change IV
    
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv=static_iv)
    padded_data = data + ' ' * (16 - len(data) % 16)
    encrypted = cipher.encrypt(padded_data.encode())
    
    return jsonify({
        'algorithm': 'AES-128-CBC',
        'iv': base64.b64encode(static_iv).decode(),
        'key': key,
        'encrypted': base64.b64encode(encrypted).decode(),
        'warning': 'Static IV allows attackers to detect when same message is sent'
    })

# 78. Predictable Key Generation
@app.route('/api/v1/crypto/generate-key', methods=['POST'])
def api_generate_key():
    # VULNERABLE: Predictable key generation
    import hashlib
    
    password = request.json.get('password', 'password123')
    salt = request.json.get('salt', 'fixed_salt')  # Static salt
    
    # Single round MD5 - easily brute forced
    key = hashlib.md5((password + salt).encode()).hexdigest()
    
    return jsonify({
        'key': key,
        'algorithm': 'MD5',
        'rounds': 1,
        'salt': salt,
        'predictable': True,
        'warning': 'Single round MD5 with fixed salt - rainbow table attack possible'
    })

# 79. Weak Hashing Algorithm (MD5/SHA1)
@app.route('/api/v1/crypto/hash', methods=['POST'])
def api_weak_hash():
    import hashlib
    
    data = request.json.get('data', '')
    algorithm = request.json.get('algorithm', 'md5')  # Default to weak MD5
    
    if algorithm == 'md5':
        hash_value = hashlib.md5(data.encode()).hexdigest()
        collision_vulnerable = True
    elif algorithm == 'sha1':
        hash_value = hashlib.sha1(data.encode()).hexdigest()
        collision_vulnerable = True
    else:
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        collision_vulnerable = False
    
    return jsonify({
        'algorithm': algorithm,
        'hash': hash_value,
        'collision_vulnerable': collision_vulnerable,
        'warning': 'MD5 and SHA1 are vulnerable to collision attacks'
    })

# 80. Hardcoded Cryptographic Keys
@app.route('/api/v1/crypto/config')
def api_crypto_config():
    # VULNERABLE: Hardcoded keys exposed
    return jsonify({
        'encryption_keys': {
            'primary': 'AES256Key2024!@#$%^&*()_+',
            'secondary': 'backup_key_1234567890',
            'legacy_des': 'deskey12'
        },
        'hmac_secrets': {
            'jwt_secret': 'jwt-signing-secret-2024',
            'api_signature': 'api-hmac-secret-key',
            'webhook_secret': 'webhook-verification-secret'
        },
        'key_rotation': {
            'last_rotation': '2020-01-01',  # Never rotated
            'next_rotation': 'none',
            'auto_rotation': False
        },
        'note': 'Keys hardcoded in source code - never use in production'
    })

# ============================================================================
# Phase 7: Expanded SSRF & Internal Scanning
# ============================================================================

# 81. SSRF - Internal Port Scanning
@app.route('/api/v1/proxy/fetch', methods=['POST'])
def api_proxy_fetch():
    # VULNERABLE: SSRF with internal network access
    url = request.json.get('url', '')
    
    # No URL validation - can access internal services
    # Examples of attacks:
    # http://localhost:22 - SSH banner grabbing
    # http://169.254.169.254 - AWS metadata
    # http://internal-api:8080 - Internal services
    
    allowed_schemes = ['http', 'https', 'ftp', 'file', 'dict', 'gopher']  # Dangerous schemes allowed
    
    return jsonify({
        'requested_url': url,
        'allowed_schemes': allowed_schemes,
        'blocking': False,
        'restriction': 'none',
        'accessible_targets': [
            'http://localhost:5000',
            'http://127.0.0.1:3306',
            'http://192.168.1.1',
            'http://169.254.169.254/latest/meta-data/',  # AWS metadata
            'file:///etc/passwd',
            'dict://localhost:11211/stat'  # Memcached
        ],
        'note': 'SSRF vulnerability - can scan internal network and access cloud metadata'
    })

# 82. Cloud Metadata Access
@app.route('/api/v1/cloud/metadata')
def api_cloud_metadata():
    # VULNERABLE: Exposes cloud metadata endpoint info
    return jsonify({
        'metadata_endpoints': {
            'aws': {
                'url': 'http://169.254.169.254/latest/meta-data/',
                'iam_credentials': 'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                'user_data': 'http://169.254.169.254/latest/user-data'
            },
            'gcp': {
                'url': 'http://metadata.google.internal/computeMetadata/v1/',
                'token': 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'
            },
            'azure': {
                'url': 'http://169.254.169.254/metadata/instance?api-version=2021-02-01',
                'token': 'http://169.254.169.254/metadata/identity/oauth2/token'
            }
        },
        'exploitation': 'Use /api/v1/proxy/fetch to access these endpoints',
        'example_payload': {'url': 'http://169.254.169.254/latest/meta-data/iam/security-credentials/'}
    })

# 83. DNS Rebinding Attack Facilitation
@app.route('/api/v1/dns/lookup', methods=['POST'])
def api_dns_lookup():
    # VULNERABLE: DNS lookup without rebinding protection
    hostname = request.json.get('hostname', '')
    
    try:
        import socket
        ip = socket.gethostbyname(hostname)
        
        return jsonify({
            'hostname': hostname,
            'resolved_ip': ip,
            'dns_rebinding_vulnerable': True,
            'note': 'No DNS rebinding protection - can resolve to internal IPs after initial check',
            'attack_scenario': '1. Register domain with short TTL. 2. Initial resolution to public IP. 3. Rebind to 127.0.0.1'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 84. Blind SSRF Detection
@app.route('/api/v1/webhook/blind-ssrf', methods=['POST'])
def api_blind_ssrf():
    # VULNERABLE: Blind SSRF - no output but makes requests
    url = request.json.get('url', '')
    
    # Simulates making request without showing result
    # Attacker uses DNS logs or timing to detect internal services
    
    return jsonify({
        'webhook_registered': True,
        'url': url,
        'callback_expected': True,
        'detection_method': 'DNS exfiltration or timing attack',
        'note': 'Blind SSRF - request is made but response not shown. Use burp collaborator or DNS logs.'
    })

# ============================================================================
# End Phase 6 & 7: Cryptographic and SSRF Vulnerabilities
# ============================================================================

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
