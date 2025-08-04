#!/usr/bin/env python3
"""
Script para testar conectividade com MLflow antes de subir a API.
"""

import logging
import sys

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mlflow_connection():
    """Testa a conexão com MLflow para garantir que funcionará na API"""
    
    print("🔌 TESTANDO CONEXÃO COM MLFLOW")
    print("=" * 50)
    
    try:
        # Importar dependências
        import mlflow
        import mlflow.pyfunc
        import dagshub
        from mlflow.tracking import MlflowClient
        print("✅ Dependências MLflow carregadas com sucesso")
        
        # Configurar MLflow/DagsHub
        print("\n📡 Configurando conexão...")
        dagshub.init(repo_owner="domires", repo_name="fiap-mlops-score-model", mlflow=True)
        mlflow.set_tracking_uri("https://dagshub.com/domires/fiap-mlops-score-model.mlflow")
        
        client = MlflowClient()
        print(f"✅ MLflow URI configurado: {mlflow.get_tracking_uri()}")
        
        # Testar Model Registry
        print("\n🏪 Testando Model Registry...")
        model_name = "fiap-mlops-score-model"
        
        try:
            registered_versions = client.search_model_versions(f"name='{model_name}'")
            if registered_versions:
                latest_version = max(registered_versions, key=lambda v: int(v.version))
                print(f"✅ Modelo encontrado no Registry: v{latest_version.version}")
                
                # Testar carregamento do modelo
                model_uri = f"models:/{model_name}/{latest_version.version}"
                print(f"📦 Carregando modelo: {model_uri}")
                
                model = mlflow.pyfunc.load_model(model_uri)
                print("✅ Modelo carregado com sucesso do Registry!")
                
                return True, "registry", latest_version.version
            else:
                print("⚠️ Nenhum modelo encontrado no Registry")
        except Exception as registry_error:
            print(f"❌ Erro no Registry: {registry_error}")
        
        # Testar runs específicos como fallback
        print("\n🏃 Testando runs específicos...")
        run_ids = ["2f5087600685403383420bf1c6720ed5", "bcadaadae75c4ea499bcdad78e9a1d11"]
        
        for run_id in run_ids:
            try:
                model_uri = f"runs:/{run_id}/model"
                print(f"📦 Testando run: {run_id}")
                
                model = mlflow.pyfunc.load_model(model_uri)
                print(f"✅ Modelo carregado com sucesso do run: {run_id}")
                
                return True, "run", run_id
            except Exception as run_error:
                print(f"❌ Erro no run {run_id}: {run_error}")
                continue
        
        print("❌ Nenhum modelo pôde ser carregado do MLflow")
        return False, None, None
        
    except ImportError as import_error:
        print(f"❌ Erro de importação: {import_error}")
        print("💡 Execute: pip install -r requirements.txt")
        return False, None, None
    except Exception as general_error:
        print(f"❌ Erro geral: {general_error}")
        return False, None, None

def main():
    """Função principal"""
    print("🎯 TESTE DE CONECTIVIDADE MLFLOW")
    print("Este script verifica se o MLflow está acessível antes de subir a API\n")
    
    success, source, version = test_mlflow_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCESSO! MLflow está funcionando")
        print(f"📊 Fonte: {source}")
        print(f"📋 Versão/Run: {version}")
        print("\n✅ A API poderá usar modelos do MLflow diretamente!")
        return 0
    else:
        print("❌ FALHA! MLflow não está acessível")
        print("\n💡 SOLUÇÕES POSSÍVEIS:")
        print("1. Verificar conexão com internet")
        print("2. Instalar dependências: pip install -r requirements.txt")
        print("3. Verificar se o repositório DagsHub está acessível")
        print("\n⚠️ A API usará modelo mock se subir assim")
        return 1

if __name__ == "__main__":
    exit(main())