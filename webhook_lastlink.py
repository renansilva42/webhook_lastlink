from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def print_received_data(data, event_type="webhook"):
    """
    Função para imprimir os dados recebidos de forma organizada
    """
    print("\n" + "="*60)
    print(f"🔔 WEBHOOK LASTLINK RECEBIDO - {event_type.upper()}")
    print("="*60)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Tipo de Evento: {event_type}")
    print("\n📋 DADOS RECEBIDOS:")
    print("-"*40)
    
    # Imprimir dados de forma estruturada
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"🔸 {key}:")
                for sub_key, sub_value in value.items():
                    print(f"   └─ {sub_key}: {sub_value}")
            elif isinstance(value, list):
                print(f"🔸 {key}: [{len(value)} itens]")
                for i, item in enumerate(value[:3]):  # Mostrar apenas os 3 primeiros
                    print(f"   └─ [{i}] {item}")
                if len(value) > 3:
                    print(f"   └─ ... e mais {len(value) - 3} itens")
            else:
                print(f"🔸 {key}: {value}")
    else:
        print(f"💾 Dados: {data}")
    
    print("="*60 + "\n")

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
        print("\n" + "="*60)
        print("📡 INFORMAÇÕES DO REQUEST")
        print("="*60)
        print(f"🌐 Método: {request.method}")
        print(f"🔗 URL: {request.url}")
        print(f"📝 Content-Type: {content_type}")
        print(f"🔑 Headers relevantes:")
        for header, value in headers.items():
            if header.lower() in ['user-agent', 'x-lastlink-signature', 'authorization', 'x-webhook-id']:
                print(f"   └─ {header}: {value}")
        
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
        print(f"❌ ERRO: {error_msg}")
        logger.error(error_msg)
        
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
            
            print("📦 RESUMO DO PEDIDO:")
            print("-"*30)
            print(f"🆔 ID do Pedido: {order_id}")
            print(f"📊 Status: {status}")
            print(f"👤 Cliente: {customer.get('name', 'N/A')}")
            print(f"📧 Email: {customer.get('email', 'N/A')}")
        
        return jsonify({"status": "success", "message": "Webhook de pedido processado"}), 200
        
    except Exception as e:
        print(f"❌ Erro no webhook de pedidos: {str(e)}")
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
            
            print("💳 RESUMO DO PAGAMENTO:")
            print("-"*30)
            print(f"🆔 ID do Pagamento: {payment_id}")
            print(f"💰 Valor: {amount}")
            print(f"📊 Status: {status}")
            print(f"💳 Método: {method}")
        
        return jsonify({"status": "success", "message": "Webhook de pagamento processado"}), 200
        
    except Exception as e:
        print(f"❌ Erro no webhook de pagamentos: {str(e)}")
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
            
            print("👤 RESUMO DO CLIENTE:")
            print("-"*30)
            print(f"🆔 ID do Cliente: {customer_id}")
            print(f"👤 Nome: {name}")
            print(f"📧 Email: {email}")
            print(f"⚡ Ação: {action}")
        
        return jsonify({"status": "success", "message": "Webhook de cliente processado"}), 200
        
    except Exception as e:
        print(f"❌ Erro no webhook de clientes: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    """
    return jsonify({
        "status": "healthy",
        "service": "Lastlink Webhook Service",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def index():
    """
    Página inicial com informações sobre os endpoints
    """
    endpoints = {
        "Webhook Principal": "/webhook/lastlink",
        "Webhook Pedidos": "/webhook/lastlink/orders",
        "Webhook Pagamentos": "/webhook/lastlink/payments",
        "Webhook Clientes": "/webhook/lastlink/customers",
        "Health Check": "/health"
    }
    
    return jsonify({
        "service": "Lastlink Webhook Service",
        "status": "running",
        "endpoints": endpoints,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n🚀 INICIANDO WEBHOOK LASTLINK")
    print("="*50)
    print("📡 Endpoints disponíveis:")
    print("  └─ POST /webhook/lastlink (principal)")
    print("  └─ POST /webhook/lastlink/orders")
    print("  └─ POST /webhook/lastlink/payments")
    print("  └─ POST /webhook/lastlink/customers")
    print("  └─ GET /health")
    print("  └─ GET /")
    print("="*50)
    print("🔄 Aguardando webhooks...")
    print("="*50 + "\n")
    
    # Executar o servidor
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )