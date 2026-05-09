# WARNING: Intentionally vulnerable Product Service
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.environ.get('DB_PATH', '/data/products.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        description TEXT,
        stock INTEGER
    )''')
    # Insert sample products
    conn.execute("INSERT OR IGNORE INTO products VALUES (1, 'Laptop', 999.99, 'High-end laptop', 10)")
    conn.execute("INSERT OR IGNORE INTO products VALUES (2, 'Phone', 699.99, 'Smartphone', 50)")
    conn.commit()
    conn.close()

@app.route('/list')
def list_products():
    # VULNERABLE: NoSQL-style injection via JSON parameters
    filter_param = request.args.get('filter', '{}')
    
    conn = sqlite3.connect(DB_PATH)
    # VULNERABLE: SQL Injection via filter parameter
    query = f"SELECT * FROM products WHERE name LIKE '%{filter_param}%'"
    products = conn.execute(query).fetchall()
    conn.close()
    
    return jsonify({'products': products, 'query': query})

@app.route('/search', methods=['POST'])
def search_products():
    # VULNERABLE: Mass assignment
    search_data = request.get_json()
    
    conn = sqlite3.connect(DB_PATH)
    # Build dynamic query - accepts any fields
    conditions = []
    for key, value in search_data.items():
        conditions.append(f"{key} = '{value}'")  # SQL Injection
    
    where_clause = ' AND '.join(conditions) if conditions else '1=1'
    query = f"SELECT * FROM products WHERE {where_clause}"
    
    products = conn.execute(query).fetchall()
    conn.close()
    
    return jsonify({'products': products, 'query': query})

@app.route('/<int:product_id>')
def get_product(product_id):
    # VULNERABLE: IDOR - no auth check
    conn = sqlite3.connect(DB_PATH)
    product = conn.execute(f"SELECT * FROM products WHERE id={product_id}").fetchone()
    conn.close()
    
    if product:
        return jsonify(dict(product))
    return jsonify({'error': 'Not found'}), 404

@app.route('/update-stock', methods=['POST'])
def update_stock():
    # VULNERABLE: Race condition on stock
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 0)
    
    conn = sqlite3.connect(DB_PATH)
    # Read current stock
    current = conn.execute(f"SELECT stock FROM products WHERE id={product_id}").fetchone()
    if current:
        new_stock = current[0] + quantity  # Race condition: concurrent updates can oversell
        conn.execute(f"UPDATE products SET stock={new_stock} WHERE id={product_id}")
        conn.commit()
    conn.close()
    
    return jsonify({'message': 'Stock updated', 'product_id': product_id})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
