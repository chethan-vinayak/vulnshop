# WARNING: Intentionally vulnerable Payment Service
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
STRIPE_KEY = os.environ.get('STRIPE_KEY', 'sk_test_vulnerable')

@app.route('/process', methods=['POST'])
def process_payment():
    # VULNERABLE: No validation, logs sensitive data
    data = request.get_json()
    
    card_number = data.get('card_number', '')
    amount = data.get('amount', 0)
    
    # VULNERABLE: Logs full card number
    print(f"Processing payment: Card={card_number}, Amount={amount}")
    
    # VULNERABLE: No CVV check, no address verification
    # Accepts test cards without validation
    
    return jsonify({
        'success': True,
        'transaction_id': f'txn_{int(time.time())}',
        'amount': amount,
        'card_last4': card_number[-4:] if len(card_number) >= 4 else '0000',
        'logged_data': f'Full card was logged: {card_number}'  # VULNERABLE: Exposes logging
    })

@app.route('/refund', methods=['POST'])
def refund():
    # VULNERABLE: Double refund attack
    order_id = request.json.get('order_id')
    amount = request.json.get('amount')
    
    # No check if already refunded
    return jsonify({
        'refunded': True,
        'order_id': order_id,
        'amount': amount,
        'refund_count': 'not_tracked',  # VULNERABLE: No tracking
        'note': 'Can refund same order multiple times'
    })

@app.route('/debug')
def debug():
    # VULNERABLE: Exposes payment configuration
    return jsonify({
        'stripe_key': STRIPE_KEY,
        'environment': 'production',
        'pci_compliance': False,
        'encryption': 'none'
    })

import time

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
