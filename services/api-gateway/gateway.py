# WARNING: Intentionally vulnerable API Gateway
# This microservice acts as a vulnerable entry point for the microservices architecture

from flask import Flask, request, jsonify, make_response
import requests
import jwt
import os
import re

app = Flask(__name__)

# Service URLs from environment
AUTH_SERVICE = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:5001')
PRODUCT_SERVICE = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:5002')
ORDER_SERVICE = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:5003')

# VULNERABLE: Hardcoded JWT secret
JWT_SECRET = 'gateway-secret-123'

@app.route('/health')
def health():
    # VULNERABLE: Exposes internal service details
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'internal_services': {
            'auth': AUTH_SERVICE,
            'products': PRODUCT_SERVICE,
            'orders': ORDER_SERVICE
        },
        'version': '1.0.0-vulnerable'
    })

@app.route('/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(path):
    # VULNERABLE: SSRF - no URL validation, can proxy to internal services
    # Can be used to scan internal network
    
    service = request.args.get('service', 'products')
    
    # VULNERABLE: Direct string concatenation for URL
    if service == 'auth':
        target_url = f"{AUTH_SERVICE}/{path}"
    elif service == 'products':
        target_url = f"{PRODUCT_SERVICE}/{path}"
    elif service == 'orders':
        target_url = f"{ORDER_SERVICE}/{path}"
    else:
        # VULNERABLE: Allows arbitrary URL
        target_url = f"{service}/{path}"
    
    try:
        # Forward request without validation
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30  # Long timeout allows slow attacks
        )
        
        # VULNERABLE: Returns all headers including internal ones
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = make_response(resp.content, resp.status_code)
        for name, value in headers:
            response.headers[name] = value
        
        return response
        
    except Exception as e:
        # VULNERABLE: Verbose error disclosure
        return jsonify({
            'error': str(e),
            'target_url': target_url,
            'traceback': 'Internal service connection failed'
        }), 500

@app.route('/internal/debug')
def internal_debug():
    # VULNERABLE: Exposes all environment variables and configuration
    return jsonify({
        'environment': dict(os.environ),
        'request_headers': dict(request.headers),
        'remote_addr': request.remote_addr,
        'internal_services': {
            'auth': AUTH_SERVICE,
            'products': PRODUCT_SERVICE,
            'orders': ORDER_SERVICE
        },
        'jwt_secret': JWT_SECRET  # VULNERABLE: Exposed secret
    })

@app.route('/internal/routes')
def internal_routes():
    # VULNERABLE: Lists all internal routes
    return jsonify({
        'routes': [
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/refresh',
            '/api/v1/products/list',
            '/api/v1/products/search',
            '/api/v1/orders/create',
            '/api/v1/orders/list',
            '/internal/debug',
            '/internal/routes',
            '/health'
        ],
        'vulnerable_endpoints': [
            '/api/v1/proxy?service=http://internal-service',
            '/internal/debug?show_secrets=true'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
