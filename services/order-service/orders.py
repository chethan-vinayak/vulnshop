# WARNING: Intentionally vulnerable Order Service
from flask import Flask, request, jsonify
import sqlite3
import os
import requests

app = Flask(__name__)
DB_PATH = os.environ.get('DB_PATH', '/data/orders.db')
PAYMENT_URL = os.environ.get('PAYMENT_GATEWAY_URL', 'http://payment-service:5004')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total REAL,
        status TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/create', methods=['POST'])
def create_order():
    # VULNERABLE: Price manipulation - accepts client-side price
    data = request.get_json()
    user_id = data.get('user_id', 1)
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    client_price = data.get('price', 99.99)  # VULNERABLE: Client sets price
    
    total = quantity * client_price  # No server-side price validation
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"INSERT INTO orders (user_id, product_id, quantity, total, status) VALUES ({user_id}, {product_id}, {quantity}, {total}, 'pending')")
    conn.commit()
    order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    
    # Call payment service
    try:
        payment_resp = requests.post(f"{PAYMENT_URL}/process", json={
            'order_id': order_id,
            'amount': total,
            'card_number': data.get('card_number')
        }, timeout=5)
    except:
        pass
    
    return jsonify({
        'order_id': order_id,
        'total': total,
        'status': 'created',
        'warning': 'Price accepted from client without validation'
    })

@app.route('/list')
def list_orders():
    # VULNERABLE: IDOR - can list any user's orders
    user_id = request.args.get('user_id')
    
    conn = sqlite3.connect(DB_PATH)
    if user_id:
        query = f"SELECT * FROM orders WHERE user_id={user_id}"
    else:
        query = "SELECT * FROM orders"  # Returns all orders
    
    orders = conn.execute(query).fetchall()
    conn.close()
    
    return jsonify({'orders': orders, 'query': query})

@app.route('/<int:order_id>/modify', methods=['POST'])
def modify_order(order_id):
    # VULNERABLE: Can modify already completed orders
    data = request.get_json()
    new_status = data.get('status', 'completed')
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"UPDATE orders SET status='{new_status}' WHERE id={order_id}")
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Order modified', 'order_id': order_id, 'new_status': new_status})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
