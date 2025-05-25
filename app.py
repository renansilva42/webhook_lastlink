#!/usr/bin/env python3
"""
Custom Webhook Receiver
Um webhook poderoso e flexível para receber dados de fontes externas em tempo real.
Compatível com EasyPanel e outros ambientes de deployment.
"""

import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs
import hashlib
import hmac

# Configuração da aplicação
app = Flask(__name__)

# Configuração de logging para EasyPanel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Para logs do EasyPanel
        logging.FileHandler('webhook.log')  # Backup em arquivo
    ]
)

logger = logging.getLogger(__name__)

# Configurações via variáveis de ambiente
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')  # Para verificação de segurança
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN', '')   # Token de autenticação
PORT = int(os.getenv('PORT', 8080))
HOST = os.getenv('HOST', '0.0.0.0')

def log_request_details(request_data, content_type, headers, source_ip):
    """Log detalhado dos dados recebidos"""
    separator = "=" * 80
    
    logger.info(f"\n{separator}")
    logger.info("🔔 WEBHOOK DATA RECEIVED")
    logger.info(f"{separator}")
    logger.info(f"📅 Timestamp: {datetime.now().isoformat()}")
    logger.info(f"🌐 Source IP: {source_ip}")
    logger.info(f"📋 Content-Type: {content_type}")
    logger.info(f"📊 Data Size: {len(str(request_data))} characters")
    
    # Log headers importantes
    important_headers = ['user-agent', 'x-forwarded-for', 'authorization', 
                        'x-hub-signature', 'x-github-event', 'x-gitlab-event']
    
    logger.info("📋 Headers:")
    for header in important_headers:
        if header in headers:
            logger.info(f"  {header}: {headers[header]}")
    
    # Log dos dados recebidos
    logger.info("📦 Data Received:")
    logger.info("-" * 40)
    
    if isinstance(request_data, dict):
        logger.info(json.dumps(request_data, indent=2, ensure_ascii=False))
    else:
        logger.info(str(request_data))
    
    logger.info(f"{separator}\n")

def verify_signature(payload, signature, secret):
    """Verifica assinatura HMAC para segurança (GitHub, GitLab style)"""
    if not secret or not signature:
        return True
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f'sha256={expected_signature}', signature)

def parse_xml_to_dict(xml_string):
    """Converte XML para dicionário"""
    try:
        root = ET.fromstring(xml_string)
        
        def xml_to_dict(element):
            result = {}
            
            # Adiciona atributos
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # Adiciona texto se existir
            if element.text and element.text.strip():
                if len(element) == 0:
                    return element.text.strip()
                result['#text'] = element.text.strip()
            
            # Adiciona elementos filhos
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        return {root.tag: xml_to_dict(root)}
    except ET.ParseError as e:
        logger.error(f"XML Parse Error: {e}")
        return {"error": "Invalid XML", "raw_data": xml_string}

@app.before_request
def log_request_info():
    """Log informações básicas de cada request"""
    logger.info(f"📨 Incoming request: {request.method} {request.path} from {request.remote_addr}")

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    """Endpoint principal do webhook"""
    try:
        # Verificação de autenticação por token
        if WEBHOOK_TOKEN:
            auth_header = request.headers.get('Authorization', '')
            provided_token = auth_header.replace('Bearer ', '').replace('Token ', '')
            
            if provided_token != WEBHOOK_TOKEN:
                logger.warning(f"🚫 Unauthorized webhook attempt from {request.remote_addr}")
                return jsonify({"error": "Unauthorized"}), 401

        # Captura informações da requisição
        content_type = request.content_type or 'unknown'
        headers = dict(request.headers)
        source_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Verificação de assinatura (se configurada)
        if WEBHOOK_SECRET:
            signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Signature')
            if not verify_signature(request.get_data(), signature, WEBHOOK_SECRET):
                logger.warning(f"🚫 Invalid signature from {source_ip}")
                return jsonify({"error": "Invalid signature"}), 403

        # Processamento baseado no Content-Type
        request_data = None
        
        if 'application/json' in content_type:
            try:
                request_data = request.get_json()
                if request_data is None:
                    request_data = {"raw_body": request.get_data(as_text=True)}
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                request_data = {"error": "Invalid JSON", "raw_body": request.get_data(as_text=True)}
        
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            xml_data = request.get_data(as_text=True)
            request_data = parse_xml_to_dict(xml_data)
        
        elif 'application/x-www-form-urlencoded' in content_type:
            request_data = dict(request.form)
        
        elif 'multipart/form-data' in content_type:
            request_data = {
                'form_data': dict(request.form),
                'files': [f.filename for f in request.files.values()]
            }
        
        else:
            # Dados raw para outros tipos
            raw_data = request.get_data(as_text=True)
            request_data = {
                "content_type": content_type,
                "raw_data": raw_data,
                "size": len(raw_data)
            }

        # Log detalhado dos dados recebidos
        log_request_details(request_data, content_type, headers, source_ip)
        
        # Resposta de sucesso
        response_data = {
            "status": "success",
            "message": "Webhook received successfully",
            "timestamp": datetime.now().isoformat(),
            "data_received": True,
            "content_type": content_type
        }
        
        logger.info("✅ Webhook processed successfully")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/webhook/<path:custom_path>', methods=['POST'])
def custom_webhook_receiver(custom_path):
    """Webhook com path customizado"""
    logger.info(f"📍 Custom webhook path: /{custom_path}")
    return webhook_receiver()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Custom Webhook Receiver"
    }), 200

@app.route('/info', methods=['GET'])
def webhook_info():
    """Informações sobre o webhook"""
    return jsonify({
        "service": "Custom Webhook Receiver",
        "version": "1.0.0",
        "endpoints": {
            "main_webhook": "/webhook",
            "custom_webhook": "/webhook/<custom_path>",
            "health_check": "/health",
            "info": "/info"
        },
        "supported_formats": ["JSON", "XML", "Form Data", "Multipart", "Raw Data"],
        "security": {
            "token_auth": bool(WEBHOOK_TOKEN),
            "signature_verification": bool(WEBHOOK_SECRET)
        },
        "timestamp": datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 - Path not found: {request.path}")
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/webhook", "/webhook/<custom_path>", "/health", "/info"]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"405 - Method not allowed: {request.method} {request.path}")
    return jsonify({
        "error": "Method not allowed",
        "message": "Use POST for webhook endpoints"
    }), 405

if __name__ == '__main__':
    logger.info("🚀 Starting Custom Webhook Receiver")
    logger.info(f"🌐 Server running on {HOST}:{PORT}")
    logger.info(f"🔐 Token auth: {'Enabled' if WEBHOOK_TOKEN else 'Disabled'}")
    logger.info(f"🔒 Signature verification: {'Enabled' if WEBHOOK_SECRET else 'Disabled'}")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )