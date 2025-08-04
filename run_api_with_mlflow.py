#!/usr/bin/env python3
"""
Script para subir a API de Credit Score forçando o uso do MLflow.
"""

import os
import sys
import subprocess
import json

def main():
    """Executa a API com MLflow"""
    
    print("SUBINDO API COM MLFLOW")
    print("=" * 50)
    
    # Configurar variável de ambiente para forçar MLflow
    os.environ['FORCE_MLFLOW'] = 'true'
    print("Configurado FORCE_MLFLOW=true")
    
    # Testar conectividade MLflow primeiro
    print("\n1. Testando conectividade MLflow...")
    try:
        result = subprocess.run([sys.executable, "test_mlflow_connection.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("ERRO: MLflow não está acessível!")
            print("\nOutput do teste:")
            print(result.stdout)
            print(result.stderr)
            print("\nSOLUÇÕES:")
            print("1. Verificar conexão com internet")
            print("2. Executar: pip install -r requirements.txt")
            print("3. Verificar se https://dagshub.com está acessível")
            return 1
        else:
            print("MLflow está funcionando!")
    except Exception as e:
        print(f"ERRO ao testar MLflow: {e}")
        return 1
    
    # Carregar a API
    print("\n📦 2. Carregando API com MLflow...")
    try:
        sys.path.append('src')
        import app
        
        # Verificar se o modelo foi carregado do MLflow
        source = app.model_info.get('source', 'unknown')
        if source not in ['mlflow_registry', 'mlflow_run']:
            print(f"ERRO: Modelo não foi carregado do MLflow! Fonte: {source}")
            return 1
        
        print(f"Modelo carregado do MLflow!")
        print(f"Fonte: {source}")
        print(f"Nome: {app.model_info.get('model_name', 'N/A')}")
        print(f"Versão: {app.model_info.get('version', 'N/A')}")
        
    except Exception as e:
        print(f"ERRO ao carregar API: {e}")
        print("\nIsso pode indicar que o MLflow não está funcionando corretamente")
        return 1
    
    # Testar predição
    print("\n3. Testando predição com dados de exemplo...")
    try:
        # Carregar dados de exemplo
        with open('data.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Executar predição
        response = app.handler(test_data, context=False)
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"Predição executada com sucesso!")
            print(f"Resultado: {body['prediction']}")
            print(f"Confiança: {body.get('confidence', 'N/A')}")
            print(f"Modelo: {body.get('model_name', 'N/A')} v{body.get('model_version', 'N/A')}")
        else:
            print(f"ERRO na predição: Status {response['statusCode']}")
            print(f"Resposta: {response}")
            return 1
            
    except Exception as e:
        print(f"ERRO ao testar predição: {e}")
        return 1
    
    print("\nSUCESSO! API está rodando com MLflow!")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    exit(main())