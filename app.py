from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import logging
import signal
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Handler para capturar sinais de shutdown
def signal_handler(signum, frame):
    logger.warning(f"🔥 Sinal recebido: {signum} - Aplicação sendo encerrada")
    logger.warning(f"📍 Frame: {frame}")
    sys.exit(0)

# Registrar handlers para sinais comuns
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

app = Flask(__name__)

def print_received_data(data, event_type="webhook"):
    """
    Função para imprimir os dados recebidos de forma organizada
    """
    logger.info("\n" + "="*60)
    logger.info(f"🔔 WEBHOOK LASTLINK RECEBIDO - {event_type.upper()}")
    logger.info("="*60)
    logger.info(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📊 Tipo de Evento: {event_type}")
    logger.info("\n📋 DADOS RECEBIDOS:")
    logger.info("-"*40)
    
    # Imprimir dados de forma estruturada
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                logger.info(f"🔸 {key}:")
                for sub_key, sub_value in value.items():
                    logger.info(f"   └─ {sub_key}: {sub_value}")
            elif isinstance(value, list):
                logger.info(f"🔸 {key}: [{len(value)} itens]")
                for i, item in enumerate(value[:3]):  # Mostrar apenas os 3 primeiros
                    logger.info(f"   └─ [{i}] {item}")
                if len(value) > 3:
                    logger.info(f"   └─ ... e mais {len(value) - 3} itens")
            else:
                logger.info(f"🔸 {key}: {value}")
    else:
        logger.info(f"💾 Dados: {data}")
    
    logger.info("="*60 + "\n")

@app.route('/', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    """
    logger.info("🩺 Health check acessado")
    return jsonify({
        "status": "online",
        "service": "Lastlink Webhook Receiver",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "endpoints": [
            "/webhook/lastlink",
            "/webhook/lastlink/orders", 
            "/webhook/lastlink/payments",
            "/webhook/lastlink/customers"
        ]
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint alternativo de health check
    """
    logger.info("🩺 Health endpoint acessado")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid()
    }), 200

@app.route('/webhook/lastlink', methods=['POST'])
def lastlink_webhook():
    """
    Endpoint principal para receber webhooks da Lastlink
    """
    try:
        # Obter dados do request
        content_type = request.content_type
        headers = dict(request.headers)
        
        # Processar dados baseado no Content-Type
        if content_type and 'application/json' in content_type:
            data = request.get_json()
        else:
            data = request.form.to_dict() if request.form else request.get_data(as_text=True)
        
        # Imprimir informações do cabeçalho
        logger.info("\n" + "="*60)
        logger.info("📡 INFORMAÇÕES DO REQUEST")
        logger.info("="*60)
        logger.info(f"🌐 Método: {request.method}")
        logger.info(f"🔗 URL: {request.url}")
        logger.info(f"📝 Content-Type: {content_type}")
        logger.info(f"🔑 Headers relevantes:")
        for header, value in headers.items():
            if header.lower() in ['user-agent', 'x-lastlink-signature', 'authorization', 'x-webhook-id']:
                logger.info(f"   └─ {header}: {value}")
        
        # Identificar tipo de evento (se disponível nos headers ou dados)
        event_type = headers.get('X-Event-Type', 'unknown')
        if isinstance(data, dict):
            event_type = data.get('event_type', data.get('type', event_type))
        
        # Imprimir dados recebidos
        print_received_data(data, event_type)
        
        # Log para arquivo também
        logger.info(f"Webhook recebido - Tipo: {event_type}, Dados: {json.dumps(data, default=str, ensure_ascii=False)}")
        
        # Resposta de sucesso
        return jsonify({
            "status": "success",
            "message": "Webhook recebido com sucesso",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type
        }), 200
        
    except Exception as e:
        error_msg = f"Erro ao processar webhook: {str(e)}"
        logger.error(f"❌ ERRO: {error_msg}")
        
        return jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/webhook/lastlink/orders', methods=['POST'])
def lastlink_orders_webhook():
    """
    Endpoint específico para webhooks de pedidos
    """
    try:
        data = request.get_json()
        print_received_data(data, "order")
        
        # Processar dados específicos de pedidos
        if data and isinstance(data, dict):
            order_id = data.get('order_id', data.get('id'))
            status = data.get('status')
            customer = data.get('customer', {})
            
            logger.info("📦 RESUMO DO PEDIDO:")
            logger.info("-"*30)
            logger.info(f"🆔 ID do Pedido: {order_id}")
            logger.info(f"📊 Status: {status}")
            logger.info(f"👤 Cliente: {customer.get('name', 'N/A')}")
            logger.info(f"📧 Email: {customer.get('email', 'N/A')}")
        
        return jsonify({"status": "success", "message": "Webhook de pedido processado"}), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook de pedidos: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/webhook/lastlink/payments', methods=['POST'])
def lastlink_payments_webhook():
    """
    Endpoint específico para webhooks de pagamentos
    """
    try:
        data = request.get_json()
        print_received_data(data, "payment")
        
        # Processar dados específicos de pagamentos
        if data and isinstance(data, dict):
            payment_id = data.get('payment_id', data.get('id'))
            amount = data.get('amount')
            status = data.get('status')
            method = data.get('payment_method')
            
            logger.info("💳 RESUMO DO PAGAMENTO:")
            logger.info("-"*30)
            logger.info(f"🆔 ID do Pagamento: {payment_id}")
            logger.info(f"💰 Valor: {amount}")
            logger.info(f"📊 Status: {status}")
            logger.info(f"💳 Método: {method}")
        
        return jsonify({"status": "success", "message": "Webhook de pagamento processado"}), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook de pagamentos: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/webhook/lastlink/customers', methods=['POST'])
def lastlink_customers_webhook():
    """
    Endpoint específico para webhooks de clientes
    """
    try:
        data = request.get_json()
        print_received_data(data, "customer")
        
        # Processar dados específicos de clientes
        if data and isinstance(data, dict):
            customer_id = data.get('customer_id', data.get('id'))
            name = data.get('name')
            email = data.get('email')
            action = data.get('action', 'unknown')
            
            logger.info("👤 RESUMO DO CLIENTE:")
            logger.info("-"*30)
            logger.info(f"🆔 ID do Cliente: {customer_id}")
            logger.info(f"👤 Nome: {name}")
            logger.info(f"📧 Email: {email}")
            logger.info(f"⚡ Ação: {action}")
        
        return jsonify({"status": "success", "message": "Webhook de cliente processado"}), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook de clientes: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# Log de inicialização apenas uma vez para evitar spam nos logs
if not hasattr(print_received_data, '_logged'):
    port = os.getenv('PORT', '5001')
    logger.info(f"🚀 Webhook Lastlink inicializado na porta {port}")
    logger.info("📡 Endpoints: /, /health, /webhook/lastlink/*")
    print_received_data._logged = True

# REMOVIDO: app.run() - o Gunicorn gerencia a execução
# Quando usar Gunicorn, não incluir app.run()

if __name__ == '__main__':
    # Este bloco só será executado se rodar diretamente com Python
    # Para desenvolvimento local apenas
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)