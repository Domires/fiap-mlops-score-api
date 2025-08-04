"""
Testes para a API de Classificação de Credit Score.
"""

import json
import os
import pytest
import src.app as app

def test_credit_score_prediction():
    """Teste básico de predição de credit score."""
    # Carrega dados de exemplo
    with open("data.json", "r", encoding="utf-8") as file:
        data = file.read()
    
    event = json.loads(data)
    print("Evento de teste:", event)
    
    # Executa predição
    response = app.handler(event, context=False)
    print("Resposta:", response)
    
    # Validações básicas
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "prediction" in body
    assert body["prediction"] in ["Good", "Standard", "Poor"]
    assert "model_version" in body
    assert "timestamp" in body
    
    return response

def test_invalid_data():
    """Teste com dados inválidos."""
    invalid_event = {
        "data": {
            "Age": "invalid",  # Valor inválido
            "Annual_Income": -1000  # Valor negativo
        }
    }
    
    response = app.handler(invalid_event, context=False)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body

def test_missing_data():
    """Teste com dados faltando - API preenche valores padrão."""
    missing_event = {
        "data": {
            "Age": 30
            # Faltam campos - API preenche automaticamente
        }
    }
    
    response = app.handler(missing_event, context=False)
    # API reformulada é robusta e preenche valores padrão
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "prediction" in body
    assert body["prediction"] in ["Good", "Standard", "Poor"]

def test_edge_cases():
    """Teste com casos extremos válidos."""
    edge_event = {
        "data": {
            "Age": 18,  # Idade mínima
            "Annual_Income": 0,
            "Monthly_Inhand_Salary": 0,
            "Num_Bank_Accounts": 0,
            "Num_Credit_Card": 0,
            "Interest_Rate": 0,
            "Num_of_Loan": 0,
            "Outstanding_Debt": 0,
            "Credit_Utilization_Ratio": 0,
            "Total_EMI_per_month": 0,
            "Amount_invested_monthly": 0,
            "Monthly_Balance": 0,
            "Occupation": "Student",
            "Credit_Mix": "Poor",
            "Payment_of_Min_Amount": "Yes",
            "Payment_Behaviour": "High_spent_Small_value_payments"
        }
    }
    
    response = app.handler(edge_event, context=False)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["prediction"] in ["Good", "Standard", "Poor"]

def test_api_gateway_format():
    """Teste com formato do API Gateway."""
    with open("data.json", "r", encoding="utf-8") as file:
        data = file.read()
    
    # Simula formato do API Gateway
    api_gateway_event = {
        "body": data,
        "headers": {"Content-Type": "application/json"}
    }
    
    response = app.handler(api_gateway_event, context=False)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "prediction" in body

if __name__ == "__main__":
    print("Executando testes da API de Credit Score...")
    
    print("\n1. Teste básico de predição:")
    test_credit_score_prediction()
    print("✅ Teste básico passou!")
    
    print("\n2. Teste com dados inválidos:")
    test_invalid_data()
    print("✅ Teste de validação passou!")
    
    print("\n3. Teste com dados faltando:")
    test_missing_data()
    print("✅ Teste de campos obrigatórios passou!")
    
    print("\n4. Teste com casos extremos:")
    test_edge_cases()
    print("✅ Teste de casos extremos passou!")
    
    print("\n5. Teste formato API Gateway:")
    test_api_gateway_format()
    print("✅ Teste API Gateway passou!")
    
    print("\n🎉 Todos os testes passaram com sucesso!")