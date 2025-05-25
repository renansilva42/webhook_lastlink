# 🔗 Webhook Receiver - Lastlink

Sistema de recepção e processamento de webhooks da plataforma Lastlink, desenvolvido em Flask e otimizado para deploy no EasyPanel.

## 📋 Funcionalidades

- ✅ **Recepção de webhooks** da Lastlink
- 📦 **Endpoints específicos** para diferentes tipos de eventos
- 🔍 **Logging detalhado** de todas as requisições
- 🩺 **Health checks** para monitoramento
- 🛡️ **Tratamento de erros** robusto
- 📊 **Análise estruturada** dos dados recebidos

## 🚀 Endpoints Disponíveis

### Health Checks
- `GET /` - Status geral da aplicação
- `GET /health` - Health check simplificado

### Webhooks
- `POST /webhook/lastlink` - **Endpoint principal** para todos os webhooks
- `POST /webhook/lastlink/orders` - Webhooks específicos de pedidos
- `POST /webhook/lastlink/payments` - Webhooks específicos de pagamentos  
- `POST /webhook/lastlink/customers` - Webhooks específicos de clientes

## 📡 Exemplo de Uso

### Testando Health Check
```bash
curl https://seu-dominio.com/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-25T10:30:00",
  "pid": 12345
}
```

### Enviando Webhook de Teste
```bash
curl -X POST https://seu-dominio.com/webhook/lastlink \
  -H "Content-Type: application/json" \
  -H "X-Event-Type: order.created" \
  -d '{
    "event_type": "order.created",
    "order_id": "ORD-12345",
    "status": "pending",
    "customer": {
      "name": "João Silva",
      "email": "joao@exemplo.com"
    },
    "amount": 99.90,
    "created_at": "2025-05-25T10:30:00Z"
  }'
```

## 🏗️ Estrutura do Projeto

```
webhook-lastlink/
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── Procfile           # Configuração para EasyPanel
├── runtime.txt        # Versão do Python
└── README.md          # Esta documentação
```

## 🛠️ Tecnologias Utilizadas

- **Flask 3.0.3** - Framework web
- **Gunicorn 22.0.0** - Servidor WSGI para produção
- **Python 3.11.9** - Linguagem de programação
- **EasyPanel** - Plataforma de deploy

## 📦 Instalação Local

### Pré-requisitos
- Python 3.11+
- pip

### Passos
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/webhook-lastlink.git
   cd webhook-lastlink
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   python app.py
   ```

A aplicação estará disponível em `http://localhost:5001`

## 🌐 Deploy no EasyPanel

### Configuração Automática
O projeto está configurado para deploy automático no EasyPanel via GitHub.

### Configurações Necessárias

**1. Health Check:**
- **Path:** `/health`
- **Initial delay:** 30 segundos
- **Interval:** 30 segundos
- **Timeout:** 10 segundos
- **Retries:** 3

**2. Variáveis de Ambiente (opcionais):**
```env
PYTHONUNBUFFERED=1
```

### Arquivos de Configuração
- **`Procfile`** - Define como iniciar a aplicação
- **`requirements.txt`** - Lista as dependências
- **`runtime.txt`** - Especifica a versão do Python

## 📊 Logs e Monitoramento

### Formato dos Logs
A aplicação gera logs estruturados para facilitar o monitoramento:

```
2025-05-25 10:30:00,123 - INFO - 🔔 WEBHOOK LASTLINK RECEBIDO - ORDER
============================================================
📅 Timestamp: 2025-05-25 10:30:00
📊 Tipo de Evento: order.created
📋 DADOS RECEBIDOS:
----------------------------------------
🔸 order_id: ORD-12345
🔸 status: pending
🔸 customer:
   └─ name: João Silva
   └─ email: joao@exemplo.com
============================================================
```

### Informações Capturadas
- **Timestamp** de recebimento
- **Headers HTTP** relevantes
- **Tipo de evento** (se fornecido)
- **Dados estruturados** do payload
- **Informações de debug** (PID, método, URL)

## 🔧 Desenvolvimento

### Estrutura do Código
- **`print_received_data()`** - Formatar e exibir dados recebidos
- **`health_check()`** - Endpoint de verificação de saúde
- **`lastlink_webhook()`** - Processador principal de webhooks
- **Endpoints específicos** - Processadores por tipo de evento

### Adicionando Novos Endpoints
```python
@app.route('/webhook/lastlink/novo-tipo', methods=['POST'])
def novo_tipo_webhook():
    try:
        data = request.get_json()
        print_received_data(data, "novo-tipo")
        
        # Sua lógica específica aqui
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
```

## 🛡️ Segurança

### Medidas Implementadas
- ✅ **Validação de dados** de entrada
- ✅ **Tratamento de exceções** robusto
- ✅ **Logs seguros** (sem dados sensíveis)
- ✅ **Headers de segurança** capturados

### Recomendações Adicionais
- Configure **autenticação por webhook signature** se disponível
- Use **HTTPS** em produção (configurado automaticamente no EasyPanel)
- Monitore **rate limiting** se necessário
- Implemente **validação de IP** se os webhooks vierem de IPs fixos

## 📈 Monitoramento e Alertas

### Métricas Importantes
- **Taxa de sucesso** dos webhooks (200 vs 4xx/5xx)
- **Tempo de resposta** médio
- **Volume de webhooks** por período
- **Tipos de evento** mais frequentes

### Health Checks
O endpoint `/health` retorna:
- **Status da aplicação**
- **Timestamp atual**
- **PID do processo**
- **Lista de endpoints disponíveis**

## 🐛 Troubleshooting

### Problemas Comuns

**1. Aplicação não inicia:**
- Verifique se o `Procfile` existe
- Confirme que `requirements.txt` está correto
- Veja os logs de build no EasyPanel

**2. Webhooks não são recebidos:**
- Teste o health check primeiro
- Verifique a URL configurada na Lastlink
- Analise os logs para ver se as requisições estão chegando

**3. Logs não aparecem:**
- Verifique o nível de log (INFO)
- Confirme que `PYTHONUNBUFFERED=1` está definido

### Comandos Úteis
```bash
# Testar localmente
python app.py

# Verificar dependências
pip list

# Testar webhook localmente
curl -X POST http://localhost:5001/webhook/lastlink \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 📞 Suporte

### Informações de Debug
Ao reportar problemas, inclua:
- **Logs completos** do erro
- **Payload do webhook** que causou o problema
- **Headers HTTP** da requisição
- **Timestamp** do incidente

### Contato
- **Repositório:** [GitHub](https://github.com/seu-usuario/webhook-lastlink)
- **Documentação Lastlink:** [Link para docs]

---

## 📝 Changelog

### v1.0.0 (2025-05-25)
- ✅ Implementação inicial
- ✅ Endpoints básicos de webhook
- ✅ Health checks
- ✅ Logging estruturado
- ✅ Deploy automatizado no EasyPanel

---

**🚀 Sistema em produção e monitorado 24/7**