# WARNING: Intentionally vulnerable Admin Panel - Full access, no auth
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Internal service URLs
SERVICES = {
    'auth': 'http://auth-service:5001',
    'products': 'http://product-service:5002',
    'orders': 'http://order-service:5003',
    'payment': 'http://payment-service:5004'
}

@app.route('/')
def admin_dashboard():
    # VULNERABLE: No authentication required
    return jsonify({
        'panel': 'VulnShop Admin',
        'access_level': 'super_admin',
        'endpoints': {
            'users': '/users',
            'database': '/database',
            'config': '/config',
            'logs': '/logs',
            'shell': '/shell'
        },
        'warning': 'No authentication - anyone can access'
    })

@app.route('/users')
def list_all_users():
    # VULNERABLE: Lists all users from auth service
    try:
        resp = requests.get(f"{SERVICES['auth']}/debug")
        return jsonify(resp.json())
    except:
        return jsonify({'error': 'Auth service unavailable'})

@app.route('/database')
def database_admin():
    # VULNERABLE: Direct database operations
    return jsonify({
        'databases': {
            'auth': 'sqlite:///data/auth.db',
            'products': 'sqlite:///data/products.db',
            'orders': 'sqlite:///data/orders.db',
            'postgres': 'postgresql://admin:admin123@internal-db:5432/vulnshop_internal'
        },
        'operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP'],
        'note': 'Full database access granted'
    })

@app.route('/config')
def show_config():
    # VULNERABLE: Exposes all environment variables and secrets
    return jsonify({
        'environment': dict(os.environ),
        'services': SERVICES,
        'internal_network': '192.168.0.0/16',
        'vpn_config': 'Disabled'
    })

@app.route('/shell', methods=['POST'])
def remote_shell():
    # VULNERABLE: Remote command execution
    command = request.json.get('command', '')
    
    # Intentionally dangerous
    return jsonify({
        'executed': True,
        'command': command,
        'output': f'Executed: {command}',
        'user': 'root',
        'warning': 'RCE vulnerability - arbitrary command execution'
    })

@app.route('/logs')
def view_logs():
    # VULNERABLE: Exposes all service logs
    return jsonify({
        'logs': {
            'auth': ['[ERROR] Password login failed for admin', '[INFO] Token generated'],
            'payment': ['[INFO] Card processed: 4532-****-****-1234', '[ERROR] CVV mismatch ignored'],
            'orders': ['[WARN] Price manipulation detected but allowed']
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)
