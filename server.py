"""
Servidor HTTP para a API de Credit Score.
Expõe a API em uma porta local para requisições HTTP.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar pasta src ao path
sys.path.append('src')

# Importar a API
try:
    import app as credit_api
    logger.info("API de Credit Score carregada com sucesso!")
except Exception as e:
    logger.error(f"Erro ao carregar API: {e}")
    sys.exit(1)

# Criar aplicação Flask
app = Flask(__name__)
CORS(app)  # Permitir CORS para requisições do frontend

@app.route('/', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "service": "Credit Score API",
        "model": credit_api.model_info.get('model_name', 'N/A'),
        "version": credit_api.model_info.get('version', 'N/A'),
        "source": credit_api.model_info.get('source', 'N/A')
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint principal para predição de credit score"""
    try:
        # Obter dados da requisição
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"error": "Content-Type deve ser application/json"}), 400
        
        # Validar se tem o campo 'data'
        if 'data' not in data:
            return jsonify({"error": "Campo 'data' é obrigatório"}), 400
        
        # Criar evento no formato esperado pela API
        event = {
            "body": json.dumps(data),
            "headers": {"Content-Type": "application/json"}
        }
        
        # Executar predição usando a API existente
        response = credit_api.handler(event, context=None)
        
        # Retornar resposta
        if response["statusCode"] == 200:
            body = json.loads(response["body"])
            return jsonify(body), 200
        else:
            body = json.loads(response["body"])
            return jsonify(body), response["statusCode"]
            
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e)
        }), 500

@app.route('/predict', methods=['GET'])
def predict_info():
    """Informações sobre o endpoint de predição"""
    return jsonify({
        "endpoint": "/predict",
        "method": "POST",
        "content_type": "application/json",
        "example": {
            "data": {
                "Age": 35,
                "Annual_Income": 65000,
                "Monthly_Inhand_Salary": 5200,
                "Num_Bank_Accounts": 2,
                "Num_Credit_Card": 2,
                "Interest_Rate": 11.5,
                "Num_of_Loan": 1,
                "Outstanding_Debt": 8000,
                "Credit_Utilization_Ratio": 28.5,
                "Total_EMI_per_month": 950,
                "Amount_invested_monthly": 800,
                "Monthly_Balance": 3200,
                "Occupation": "Software Engineer",
                "Credit_Mix": "Good",
                "Payment_of_Min_Amount": "No",
                "Payment_Behaviour": "Low_spent_Medium_value_payments"
            }
        }
    })

@app.route('/model-info', methods=['GET'])
def model_info():
    """Informações sobre o modelo carregado"""
    return jsonify(credit_api.model_info)

if __name__ == '__main__':
    print("SUBINDO SERVIDOR HTTP DA API DE CREDIT SCORE")
    print("=" * 60)
    print(f"Modelo: {credit_api.model_info.get('model_name', 'N/A')}")
    print(f"Versão: {credit_api.model_info.get('version', 'N/A')}")
    print(f"Fonte: {credit_api.model_info.get('source', 'N/A')}")
    print("=" * 60)
    print("Endpoints disponíveis:")
    print("GET  / - Health check")
    print("POST /predict - Predição de credit score") 
    print("GET  /predict - Informações do endpoint")
    print("GET  /model-info - Informações do modelo")
    print("=" * 60)
    print("ervidor rodando em: http://localhost:5000")
    print("Para parar: Ctrl+C")
    print("=" * 60)
    
    # Subir servidor
    app.run(host='0.0.0.0', port=5000, debug=False)