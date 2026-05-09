# WARNING: Intentionally vulnerable Auth Service
from flask import Flask, request, jsonify
import jwt
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# VULNERABLE: Weak secrets
JWT_SECRET = os.environ.get('JWT_SECRET', 'weak-secret-123')
DB_PATH = os.environ.get('DB_PATH', '/data/auth.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        email TEXT,
        role TEXT DEFAULT 'user'
    )''')
    # Insert default vulnerable users
    conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin@vulnshop.com', 'admin')")
    conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'password', 'user@vulnshop.com', 'user')")
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    # VULNERABLE: No rate limiting, timing attack possible
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    
    conn = sqlite3.connect(DB_PATH)
    # VULNERABLE: SQL Injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = conn.execute(query).fetchone()
    conn.close()
    
    if user:
        # VULNERABLE: JWT None algorithm, weak secret, no expiration
        token = jwt.encode(
            {'user': user[1], 'role': user[4], 'exp': datetime.utcnow() + timedelta(days=365)},
            JWT_SECRET,
            algorithm='HS256'
        )
        return jsonify({'token': token, 'user': user[1], 'role': user[4]})
    
    return jsonify({'error': 'Invalid credentials', 'query': query}), 401

@app.route('/register', methods=['POST'])
def register():
    # VULNERABLE: No validation, allows duplicate usernames
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role', 'user')  # VULNERABLE: Client can set any role
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"INSERT INTO users (username, password, role) VALUES ('{username}', '{password}', '{role}')")
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User created', 'role': role})

@app.route('/verify', methods=['POST'])
def verify():
    # VULNERABLE: Accepts 'none' algorithm
    token = request.json.get('token', '')
    algorithm = request.json.get('algorithm', 'HS256')
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[algorithm], options={"verify_exp": False})
        return jsonify({'valid': True, 'payload': payload})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
