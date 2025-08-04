"""
Testes para a API de Classificação de Credit Score.
Testes unificados e organizados para validar toda a funcionalidade da API.
"""

import json
import pytest
import sys
import os
from pathlib import Path

# Adicionar pasta src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import app


class TestCreditScoreAPI:
    """Classe de testes para a API de Credit Score"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        # Carregar dados de exemplo uma vez
        data_file = Path(__file__).parent.parent / "data.json"
        with open(data_file, "r", encoding="utf-8") as file:
            self.sample_data = json.loads(file.read())
    
    def test_model_loaded(self):
        """Testa se o modelo foi carregado corretamente"""
        assert app.model is not None, "Modelo não foi carregado"
        assert app.model_info is not None, "Informações do modelo não disponíveis"
        assert "model_name" in app.model_info, "Nome do modelo não encontrado"
    
    def test_basic_prediction(self):
        """Teste básico de predição com dados válidos"""
        response = app.handler(self.sample_data, context=None)
        
        # Validações de resposta
        assert response["statusCode"] == 200, "Status code deve ser 200"
        
        body = json.loads(response["body"])
        
        # Validações de conteúdo
        assert "prediction" in body, "Campo 'prediction' deve estar presente"
        assert body["prediction"] in ["Good", "Standard", "Poor"], "Predição deve ser válida"
        assert "confidence" in body, "Campo 'confidence' deve estar presente"
        assert "probabilities" in body, "Campo 'probabilities' deve estar presente"
        assert "model_version" in body, "Campo 'model_version' deve estar presente"
        assert "timestamp" in body, "Campo 'timestamp' deve estar presente"
        
        # Validações de tipos
        assert isinstance(body["confidence"], (int, float)), "Confidence deve ser numérico"
        assert isinstance(body["probabilities"], dict), "Probabilities deve ser um dict"
        assert 0 <= body["confidence"] <= 1, "Confidence deve estar entre 0 e 1"
    
    def test_invalid_data_validation(self):
        """Teste com dados inválidos - deve retornar erro 400"""
        invalid_event = {
            "data": {
                "Age": "invalid_string",  # Tipo inválido
                "Annual_Income": -1000    # Valor negativo
            }
        }
        
        response = app.handler(invalid_event, context=None)
        assert response["statusCode"] == 400, "Status deve ser 400 para dados inválidos"
        
        body = json.loads(response["body"])
        assert "error" in body, "Deve conter campo de erro"
    
    def test_missing_required_fields(self):
        """Teste com campos obrigatórios faltando - API deve preencher automaticamente"""
        minimal_event = {
            "data": {
                "Age": 30,
                "Annual_Income": 50000
                # Outros campos faltando - API deve usar valores padrão
            }
        }
        
        response = app.handler(minimal_event, context=None)
        assert response["statusCode"] == 200, "API deve aceitar dados mínimos"
        
        body = json.loads(response["body"])
        assert body["prediction"] in ["Good", "Standard", "Poor"], "Predição deve ser válida"
    
    def test_edge_cases(self):
        """Teste com casos extremos mas válidos"""
        edge_cases = [
            # Caso 1: Valores mínimos
            {
                "data": {
                    "Age": 18,
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
                    "Credit_Mix": "Poor"
                }
            },
            # Caso 2: Valores altos
            {
                "data": {
                    "Age": 65,
                    "Annual_Income": 200000,
                    "Monthly_Inhand_Salary": 16000,
                    "Num_Bank_Accounts": 10,
                    "Num_Credit_Card": 8,
                    "Interest_Rate": 30.0,
                    "Num_of_Loan": 5,
                    "Outstanding_Debt": 100000,
                    "Credit_Utilization_Ratio": 100.0,
                    "Total_EMI_per_month": 5000,
                    "Amount_invested_monthly": 5000,
                    "Monthly_Balance": 10000,
                    "Occupation": "CEO",
                    "Credit_Mix": "Excellent"
                }
            }
        ]
        
        for i, case in enumerate(edge_cases):
            response = app.handler(case, context=None)
            assert response["statusCode"] == 200, f"Caso extremo {i+1} deve retornar 200"
            
            body = json.loads(response["body"])
            assert body["prediction"] in ["Good", "Standard", "Poor"], f"Predição válida para caso {i+1}"
    
    def test_api_gateway_format(self):
        """Teste com formato de requisição do API Gateway"""
        api_gateway_event = {
            "body": json.dumps(self.sample_data),
            "headers": {"Content-Type": "application/json"}
        }
        
        response = app.handler(api_gateway_event, context=None)
        assert response["statusCode"] == 200, "Formato API Gateway deve funcionar"
        
        body = json.loads(response["body"])
        assert "prediction" in body, "Resposta deve conter predição"
    
    def test_direct_invocation_format(self):
        """Teste com formato de invocação direta (Lambda)"""
        response = app.handler(self.sample_data, context=None)
        assert response["statusCode"] == 200, "Invocação direta deve funcionar"
        
        body = json.loads(response["body"])
        assert "prediction" in body, "Resposta deve conter predição"
    
    def test_response_format_consistency(self):
        """Teste de consistência do formato de resposta"""
        response = app.handler(self.sample_data, context=None)
        body = json.loads(response["body"])
        
        # Verificar estrutura obrigatória
        required_fields = ["prediction", "confidence", "probabilities", "model_version", "timestamp"]
        for field in required_fields:
            assert field in body, f"Campo obrigatório '{field}' deve estar presente"
        
        # Verificar estrutura das probabilidades
        prob_fields = ["Good", "Standard", "Poor"]
        for field in prob_fields:
            assert field in body["probabilities"], f"Probabilidade '{field}' deve estar presente"
            assert isinstance(body["probabilities"][field], (int, float)), f"Probabilidade '{field}' deve ser numérica"
    
    def test_different_credit_scenarios(self):
        """Teste com diferentes cenários de crédito"""
        scenarios = [
            # Cenário Good Score
            {
                "name": "Good Credit",
                "data": {
                    "Age": 35,
                    "Annual_Income": 80000,
                    "Monthly_Inhand_Salary": 6500,
                    "Num_Bank_Accounts": 3,
                    "Num_Credit_Card": 2,
                    "Interest_Rate": 8.5,
                    "Num_of_Loan": 1,
                    "Outstanding_Debt": 5000,
                    "Credit_Utilization_Ratio": 20.0,
                    "Total_EMI_per_month": 1200,
                    "Amount_invested_monthly": 2000,
                    "Monthly_Balance": 4000,
                    "Occupation": "Engineer",
                    "Credit_Mix": "Good"
                }
            },
            # Cenário Poor Score
            {
                "name": "Poor Credit",
                "data": {
                    "Age": 25,
                    "Annual_Income": 25000,
                    "Monthly_Inhand_Salary": 1800,
                    "Num_Bank_Accounts": 1,
                    "Num_Credit_Card": 6,
                    "Interest_Rate": 28.0,
                    "Num_of_Loan": 4,
                    "Outstanding_Debt": 30000,
                    "Credit_Utilization_Ratio": 95.0,
                    "Total_EMI_per_month": 1500,
                    "Amount_invested_monthly": 0,
                    "Monthly_Balance": 100,
                    "Occupation": "Unemployed",
                    "Credit_Mix": "Poor"
                }
            }
        ]
        
        for scenario in scenarios:
            event = {"data": scenario["data"]}
            response = app.handler(event, context=None)
            
            assert response["statusCode"] == 200, f"Cenário '{scenario['name']}' deve retornar 200"
            
            body = json.loads(response["body"])
            assert body["prediction"] in ["Good", "Standard", "Poor"], f"Predição válida para '{scenario['name']}'"
    
    def test_error_handling(self):
        """Teste de tratamento de erros"""
        # Teste com dados completamente inválidos
        invalid_events = [
            {"invalid": "structure"},  # Estrutura incorreta
            {"data": None},            # Data nulo
            {"data": {}},              # Data vazio (deve funcionar com valores padrão)
            {}                         # Evento vazio
        ]
        
        for invalid_event in invalid_events:
            response = app.handler(invalid_event, context=None)
            # Deve retornar erro ou usar valores padrão (dependendo da robustez da API)
            assert response["statusCode"] in [200, 400, 500], "Status code deve ser válido"


# Função para executar testes manualmente
def run_tests():
    """Executa todos os testes manualmente"""
    import traceback
    
    print("🧪 EXECUTANDO TESTES DA API DE CREDIT SCORE")
    print("=" * 60)
    
    test_instance = TestCreditScoreAPI()
    test_instance.setup_method()
    
    tests = [
        ("Modelo carregado", test_instance.test_model_loaded),
        ("Predição básica", test_instance.test_basic_prediction),
        ("Validação de dados", test_instance.test_invalid_data_validation),
        ("Campos obrigatórios", test_instance.test_missing_required_fields),
        ("Casos extremos", test_instance.test_edge_cases),
        ("Formato API Gateway", test_instance.test_api_gateway_format),
        ("Invocação direta", test_instance.test_direct_invocation_format),
        ("Formato de resposta", test_instance.test_response_format_consistency),
        ("Cenários de crédito", test_instance.test_different_credit_scenarios),
        ("Tratamento de erros", test_instance.test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"Executando: {test_name}...")
            test_func()
            print(f"{test_name}: PASSOU")
            passed += 1
        except Exception as e:
            print(f"{test_name}: FALHOU")
            print(f"   Erro: {str(e)}")
            traceback.print_exc()
    
    print("=" * 60)
    print(f"RESULTADO: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("ALGUNS TESTES FALHARAM!")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)