#!/usr/bin/env python3
"""
Simple webhook handler for Railway deployment
"""
from flask import Flask, request, jsonify
import logging
import os
import pandas as pd
from signal_generator import signal_generator
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook requests"""
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        # Process webhook data
        response = {
            'status': 'success',
            'message': 'Webhook received successfully',
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': pd.Timestamp.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'syntX_bot API',
        'status': 'running',
        'endpoints': ['/webhook', '/health', '/']
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
