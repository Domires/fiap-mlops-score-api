#!/usr/bin/env python3
"""
Teste completo do endpoint MLflow para a API de Credit Score.
Baseado na configuração real da pasta modelo.
"""

import json
import sys
import os

# Adicionar pasta src ao path
sys.path.append('src')

def test_api_with_mlflow():
    """Testa a API usando dados de exemplo e o modelo do MLflow"""
    
    print("=" * 70)
    print("🔌 TESTE COMPLETO: API + ENDPOINT MLFLOW")
    print("=" * 70)
    print()
    
    try:
        # Importar módulo da API
        import app
        
        print("✅ Módulo da API importado com sucesso")
        print(f"📊 Modelo carregado: {app.model_info}")
        print()
        
        # Dados de teste baseados na pasta modelo
        test_cases = [
            {
                "name": "Cliente Jovem - Perfil Conservador",
                "data": {
                    "Age": 25,
                    "Annual_Income": 35000,
                    "Monthly_Inhand_Salary": 2800,
                    "Num_Bank_Accounts": 1,
                    "Num_Credit_Card": 1,
                    "Interest_Rate": 18,
                    "Num_of_Loan": 0,
                    "Delay_from_due_date": 0,
                    "Num_of_Delayed_Payment": 0,
                    "Changed_Credit_Limit": 0,
                    "Num_Credit_Inquiries": 1,
                    "Outstanding_Debt": 0,
                    "Credit_Utilization_Ratio": 15.5,
                    "Total_EMI_per_month": 0,
                    "Amount_invested_monthly": 100,
                    "Monthly_Balance": 1500,
                    "Occupation": "Student",
                    "Credit_Mix": "Standard"
                }
            },
            {
                "name": "Cliente Médio - Perfil Equilibrado",
                "data": {
                    "Age": 35,
                    "Annual_Income": 60000,
                    "Monthly_Inhand_Salary": 4800,
                    "Num_Bank_Accounts": 2,
                    "Num_Credit_Card": 2,
                    "Interest_Rate": 12,
                    "Num_of_Loan": 1,
                    "Delay_from_due_date": 2,
                    "Num_of_Delayed_Payment": 1,
                    "Changed_Credit_Limit": 5,
                    "Num_Credit_Inquiries": 2,
                    "Outstanding_Debt": 5000,
                    "Credit_Utilization_Ratio": 35.0,
                    "Total_EMI_per_month": 800,
                    "Amount_invested_monthly": 500,
                    "Monthly_Balance": 2500,
                    "Occupation": "Engineer",
                    "Credit_Mix": "Good"
                }
            },
            {
                "name": "Cliente Sênior - Perfil Alto Risco",
                "data": {
                    "Age": 55,
                    "Annual_Income": 80000,
                    "Monthly_Inhand_Salary": 6500,
                    "Num_Bank_Accounts": 4,
                    "Num_Credit_Card": 5,
                    "Interest_Rate": 8,
                    "Num_of_Loan": 3,
                    "Delay_from_due_date": 10,
                    "Num_of_Delayed_Payment": 5,
                    "Changed_Credit_Limit": 15,
                    "Num_Credit_Inquiries": 8,
                    "Outstanding_Debt": 25000,
                    "Credit_Utilization_Ratio": 75.0,
                    "Total_EMI_per_month": 2000,
                    "Amount_invested_monthly": 1000,
                    "Monthly_Balance": 1000,
                    "Occupation": "Manager",
                    "Credit_Mix": "Poor"
                }
            }
        ]
        
        print("🧪 EXECUTANDO TESTES:")
        print()
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📋 TESTE {i}: {test_case['name']}")
            print("-" * 50)
            
            # Criar evento no formato da API
            event = {"data": test_case["data"]}
            
            try:
                # Chamar handler da API
                response = app.handler(event, context=None)
                
                # Verificar resposta
                if response["statusCode"] == 200:
                    body = json.loads(response["body"])
                    prediction = body.get("prediction", "N/A")
                    confidence = body.get("confidence", "N/A")
                    model_version = body.get("model_version", "N/A")
                    
                    print(f"✅ Status: {response['statusCode']} OK")
                    print(f"🎯 Predição: {prediction}")
                    if confidence != "N/A":
                        print(f"📊 Confiança: {confidence:.3f}")
                    print(f"📋 Versão do Modelo: {model_version}")
                    
                    # Mostrar probabilidades se disponível
                    if "probabilities" in body:
                        print("📊 Probabilidades:")
                        for class_name, prob in body["probabilities"].items():
                            print(f"   {class_name}: {prob:.3f}")
                    
                    print("✅ TESTE PASSOU!")
                    
                else:
                    print(f"❌ Status: {response['statusCode']}")
                    body = json.loads(response["body"])
                    print(f"❌ Erro: {body.get('error', 'Erro desconhecido')}")
                    print(f"💬 Mensagem: {body.get('message', 'N/A')}")
                    all_passed = False
                    
            except Exception as test_error:
                print(f"❌ ERRO NO TESTE: {test_error}")
                all_passed = False
            
            print()
        
        # Teste adicional: formato API Gateway
        print("🌐 TESTE ADICIONAL: Formato API Gateway")
        print("-" * 50)
        
        api_gateway_event = {
            "body": json.dumps({"data": test_cases[1]["data"]}),
            "headers": {"Content-Type": "application/json"}
        }
        
        try:
            response = app.handler(api_gateway_event, context=None)
            if response["statusCode"] == 200:
                print("✅ FORMATO API GATEWAY: OK")
            else:
                print("❌ FORMATO API GATEWAY: FALHOU")
                all_passed = False
        except Exception as gw_error:
            print(f"❌ ERRO API GATEWAY: {gw_error}")
            all_passed = False
        
        print()
        print("=" * 70)
        
        if all_passed:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ O endpoint MLflow está funcionando perfeitamente")
            print("✅ A API está pronta para produção")
        else:
            print("❌ ALGUNS TESTES FALHARAM!")
            print("💡 Verifique os erros acima")
        
        print("=" * 70)
        
        return all_passed
        
    except ImportError as import_error:
        print(f"❌ ERRO DE IMPORTAÇÃO: {import_error}")
        print("💡 Verifique se todas as dependências estão instaladas")
        print("💡 Execute: pip install -r requirements.txt")
        return False
        
    except Exception as general_error:
        print(f"❌ ERRO GERAL: {general_error}")
        return False

def test_direct_mlflow_connection():
    """Testa conexão direta com MLflow (sem API)"""
    
    print("\n🔌 TESTE DIRETO: Conexão MLflow")
    print("-" * 40)
    
    try:
        import mlflow
        import mlflow.pyfunc
        import dagshub
        import pandas as pd
        
        # Configurar MLflow
        dagshub.init(repo_owner="domires", repo_name="fiap-mlops-score-model", mlflow=True)
        mlflow.set_tracking_uri("https://dagshub.com/domires/fiap-mlops-score-model.mlflow")
        
        print(f"✅ MLflow URI: {mlflow.get_tracking_uri()}")
        
        # Testar carregamento de modelo
        run_ids = [
            "2f5087600685403383420bf1c6720ed5",
            "bcadaadae75c4ea499bcdad78e9a1d11"
        ]
        
        for run_id in run_ids:
            try:
                model_uri = f"runs:/{run_id}/model"
                model = mlflow.pyfunc.load_model(model_uri)
                print(f"✅ Modelo carregado: {run_id}")
                
                # Teste rápido
                test_data = pd.DataFrame({
                    'Age': [30],
                    'Annual_Income': [50000],
                    'Monthly_Inhand_Salary': [4000],
                    'Num_Bank_Accounts': [2],
                    'Num_Credit_Card': [1],
                    'Interest_Rate': [15],
                    'Num_of_Loan': [1],
                    'Delay_from_due_date': [0],
                    'Num_of_Delayed_Payment': [0],
                    'Changed_Credit_Limit': [0],
                    'Num_Credit_Inquiries': [1],
                    'Outstanding_Debt': [1000],
                    'Credit_Utilization_Ratio': [30],
                    'Total_EMI_per_month': [500],
                    'Amount_invested_monthly': [200],
                    'Monthly_Balance': [1500]
                })
                
                prediction = model.predict(test_data)
                print(f"✅ Predição teste: {prediction[0]}")
                return True
                
            except Exception as model_error:
                print(f"⚠️ Run {run_id}: {model_error}")
                continue
        
        print("❌ Nenhum modelo funcionou")
        return False
        
    except Exception as conn_error:
        print(f"❌ Erro de conexão: {conn_error}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO ENDPOINT MLFLOW")
    print()
    
    # Teste 1: Conexão direta
    direct_test = test_direct_mlflow_connection()
    
    # Teste 2: API completa
    if direct_test:
        api_test = test_api_with_mlflow()
        
        if api_test:
            print("\n🎯 PRÓXIMOS PASSOS:")
            print("   1. ✅ Endpoint MLflow está funcionando")
            print("   2. ✅ API está pronta para deploy")
            print("   3. 🔄 Pode integrar com aplicação Streamlit")
            print("   4. 🚀 Pronto para produção!")
        else:
            print("\n💡 AÇÕES RECOMENDADAS:")
            print("   1. Verificar dependências: pip install -r requirements.txt")
            print("   2. Testar conexão de rede com DagsHub")
            print("   3. Verificar se os modelos estão registrados no MLflow")
    else:
        print("\n💡 PROBLEMA NA CONEXÃO MLFLOW:")
        print("   1. Verificar conectividade com https://dagshub.com")
        print("   2. Verificar se o repositório existe")
        print("   3. Executar modelo/testar_endpoint_mlflow.py")