# WARNING: Intentionally vulnerable app. For local testing only. Never deploy.

import sqlite3
import os

DATABASE = 'shopzone.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT NOT NULL,
            rating REAL DEFAULT 4.0,
            reviews INTEGER DEFAULT 0
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # Seed users (plaintext passwords - intentionally vulnerable)
    cursor.execute('''
        INSERT INTO users (username, email, password) VALUES
        ('admin', 'admin@vulnshop.com', 'admin123'),
        ('testuser', 'test@vulnshop.com', 'password123')
    ''')
    
    # Seed products with images
    products = [
        ('Wireless Bluetooth Headphones', 'Premium noise-cancelling headphones with 30-hour battery life', 129.99, 'Electronics', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop', 4.5, 128),
        ('Gaming Laptop Pro', 'High-performance laptop with RTX 4060, 16GB RAM, 512GB SSD', 1299.99, 'Electronics', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&h=300&fit=crop', 4.7, 456),
        ('Smart Watch Series 5', 'Fitness tracker with heart rate monitor and GPS', 249.99, 'Electronics', 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400&h=300&fit=crop', 4.4, 2341),
        ('Men\'s Casual Denim Jacket', 'Classic blue denim jacket, comfortable fit, all seasons', 59.99, 'Clothing', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=300&fit=crop', 4.2, 567),
        ('Women\'s Summer Dress', 'Floral print maxi dress, lightweight and breathable', 39.99, 'Clothing', 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=300&fit=crop', 4.6, 823),
        ('Running Shoes Pro', 'Lightweight athletic shoes with cushioned sole', 89.99, 'Clothing', '/static/images/shoes.png', 4.5, 1456),
        ('Portable Phone Charger', '20000mAh power bank with fast charging', 29.99, 'Electronics', '/static/images/charger.png', 4.5, 1567),
        ('USB-C Hub', '7-in-1 adapter with HDMI, USB 3.0, SD card reader', 34.99, 'Electronics', '/static/images/hub.png', 4.2, 842),
        ('Leather Wallet', 'Genuine leather bifold wallet with RFID protection', 24.50, 'Accessories', '/static/images/wallet.png', 4.8, 2305),
        ('Wireless Headphones', 'Over-ear noise cancelling headphones', 89.99, 'Electronics', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop', 4.6, 5430),
        ('Digital Watch', 'Waterproof sports watch with backlight', 19.99, 'Accessories', '/static/images/watch.png', 4.1, 950),
        ('Cotton T-Shirt', 'Premium 100% cotton casual t-shirt', 14.99, 'Clothing', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=300&fit=crop', 4.7, 3210),
        ('Bluetooth Speaker', 'Portable waterproof speaker with deep bass', 45.00, 'Electronics', '/static/images/speaker.png', 4.3, 1280)
    ]
    cursor.executemany('''
        INSERT INTO products (name, description, price, category, image_url, rating, reviews) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products)
    
    # Seed orders
    cursor.execute('''
        INSERT INTO orders (user_id, product_id, quantity, status) VALUES
        (1, 1, 1, 'Delivered'),
        (1, 3, 1, 'Shipped'),
        (2, 2, 1, 'Processing'),
        (2, 5, 2, 'Delivered')
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized and seeded successfully.")

if __name__ == '__main__':
    init_db()
