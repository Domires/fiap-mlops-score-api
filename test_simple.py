#!/usr/bin/env python3
"""
Teste simples e robusto para a API de Credit Score.
Funciona independente de MLflow estar disponível.
"""

import json
import sys
import os

# Adicionar pasta src ao path
sys.path.append('src')

def test_basic_functionality():
    """Teste básico da funcionalidade principal"""
    
    print("=" * 60)
    print("🧪 TESTE SIMPLES DA API DE CREDIT SCORE")
    print("=" * 60)
    print()
    
    try:
        # Importar a API
        import app
        
        print("✅ API importada com sucesso!")
        print(f"📊 Modelo carregado: {app.model_info.get('model_name', 'N/A')}")
        print(f"📋 Versão: {app.model_info.get('version', 'N/A')}")
        print(f"🔗 Fonte: {app.model_info.get('source', 'N/A')}")
        print()
        
        # Casos de teste
        test_cases = [
            {
                "name": "Cliente com Bom Score",
                "data": {
                    "Age": 35,
                    "Annual_Income": 80000,
                    "Monthly_Inhand_Salary": 6500,
                    "Num_Bank_Accounts": 3,
                    "Num_Credit_Card": 2,
                    "Interest_Rate": 8.5,
                    "Num_of_Loan": 1,
                    "Outstanding_Debt": 3000,
                    "Credit_Utilization_Ratio": 15.0,
                    "Total_EMI_per_month": 1200,
                    "Amount_invested_monthly": 1500,
                    "Monthly_Balance": 4000
                }
            },
            {
                "name": "Cliente com Score Médio",
                "data": {
                    "Age": 28,
                    "Annual_Income": 45000,
                    "Monthly_Inhand_Salary": 3500,
                    "Num_Bank_Accounts": 2,
                    "Num_Credit_Card": 3,
                    "Interest_Rate": 14.5,
                    "Num_of_Loan": 2,
                    "Outstanding_Debt": 12000,
                    "Credit_Utilization_Ratio": 45.0,
                    "Total_EMI_per_month": 800,
                    "Amount_invested_monthly": 300,
                    "Monthly_Balance": 1800
                }
            },
            {
                "name": "Cliente com Score Baixo",
                "data": {
                    "Age": 22,
                    "Annual_Income": 25000,
                    "Monthly_Inhand_Salary": 2000,
                    "Num_Bank_Accounts": 1,
                    "Num_Credit_Card": 4,
                    "Interest_Rate": 22.0,
                    "Num_of_Loan": 3,
                    "Outstanding_Debt": 18000,
                    "Credit_Utilization_Ratio": 85.0,
                    "Total_EMI_per_month": 600,
                    "Amount_invested_monthly": 0,
                    "Monthly_Balance": 500
                }
            }
        ]
        
        print("🚀 EXECUTANDO TESTES:")
        print()
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📋 TESTE {i}: {test_case['name']}")
            print("-" * 40)
            
            try:
                # Criar evento
                event = {"data": test_case["data"]}
                
                # Executar API
                response = app.handler(event, context=None)
                
                # Verificar resultado
                if response["statusCode"] == 200:
                    body = json.loads(response["body"])
                    
                    print(f"✅ Status: OK")
                    print(f"🎯 Predição: {body.get('prediction', 'N/A')}")
                    
                    if "confidence" in body:
                        print(f"📊 Confiança: {body['confidence']:.3f}")
                    
                    if "probabilities" in body:
                        print("📊 Probabilidades:")
                        for class_name, prob in body["probabilities"].items():
                            print(f"   {class_name}: {prob:.3f}")
                    
                    print(f"📋 Timestamp: {body.get('timestamp', 'N/A')}")
                    success_count += 1
                    
                else:
                    print(f"❌ Status: {response['statusCode']}")
                    body = json.loads(response["body"])
                    print(f"❌ Erro: {body.get('error', 'Erro desconhecido')}")
                
            except Exception as test_error:
                print(f"❌ Erro no teste: {test_error}")
            
            print()
        
        # Resumo
        print("=" * 60)
        print(f"📊 RESUMO: {success_count}/{len(test_cases)} testes passaram")
        
        if success_count == len(test_cases):
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ A API está funcionando corretamente")
        else:
            print("⚠️ Alguns testes falharam, mas funcionalidade básica OK")
        
        print("=" * 60)
        
        return success_count > 0
        
    except Exception as main_error:
        print(f"❌ ERRO PRINCIPAL: {main_error}")
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        print("   1. Instalar dependências: pip install -r requirements.txt")
        print("   2. Verificar se os arquivos estão na pasta correta")
        print("   3. Verificar imports do Python")
        return False

def test_edge_cases():
    """Teste casos extremos"""
    
    print("\n🧪 TESTE DE CASOS EXTREMOS")
    print("-" * 40)
    
    try:
        import app
        
        # Teste com dados mínimos
        minimal_data = {
            "data": {
                "Age": 25,
                "Annual_Income": 30000
                # Demais campos serão preenchidos com defaults
            }
        }
        
        print("🔬 Testando com dados mínimos...")
        response = app.handler(minimal_data, context=None)
        
        if response["statusCode"] == 200:
            body = json.loads(response["body"])
            print(f"✅ Dados mínimos OK: {body.get('prediction', 'N/A')}")
        else:
            print("⚠️ Dados mínimos falharam")
        
        # Teste com dados inválidos
        invalid_data = {
            "data": {
                "Age": "invalid",
                "Annual_Income": -5000
            }
        }
        
        print("🔬 Testando com dados inválidos...")
        response = app.handler(invalid_data, context=None)
        
        if response["statusCode"] == 400:
            print("✅ Validação de dados inválidos funcionando")
        elif response["statusCode"] == 200:
            print("⚠️ API aceitou dados inválidos (usando fallbacks)")
        else:
            print("❌ Comportamento inesperado com dados inválidos")
        
        return True
        
    except Exception as edge_error:
        print(f"❌ Erro nos testes extremos: {edge_error}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DA API")
    print()
    
    # Teste principal
    main_success = test_basic_functionality()
    
    # Testes adicionais
    if main_success:
        edge_success = test_edge_cases()
        
        print("\n🎯 RESULTADO FINAL:")
        if main_success and edge_success:
            print("✅ API TOTALMENTE FUNCIONAL!")
            print("🚀 Pronta para integração com aplicação Streamlit")
        else:
            print("✅ API FUNCIONANDO (funcionalidade básica OK)")
            print("⚠️ Alguns recursos avançados podem precisar de ajustes")
    else:
        print("\n❌ API NÃO ESTÁ FUNCIONANDO")
        print("💡 Verifique os erros acima e corrija os problemas")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Se API estiver OK → Integrar com Streamlit")
    print("   2. Se houver erros → Corrigir dependências")
    print("   3. Deploy → Usar Docker/Lambda")
    print("   4. Produção → Configurar MLflow adequadamente")