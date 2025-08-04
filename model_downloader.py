"""
Script para baixar o modelo mais recente de classificação de Credit Score do MLflow.
"""

from mlflow.tracking import MlflowClient
import mlflow
import json
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_latest_model():
    """
    Baixa a versão mais recente do modelo de credit score do MLflow.
    """
    try:
        logger.info("Baixando a versão mais recente do modelo...")
        
        # Configuração do MLflow
        mlflow.set_tracking_uri("https://dagshub.com/domires/fiap-mlops-score-model.mlflow")
        
        model_name = "fiap-mlops-score-model"
        client = MlflowClient()
        
        # Busca todas as versões do modelo
        logger.info(f"Buscando versões do modelo: {model_name}")
        versions = client.search_model_versions(f"name='{model_name}'")
        
        if not versions:
            logger.error(f"Nenhuma versão encontrada para o modelo: {model_name}")
            return False
        
        # Encontra a versão mais recente
        latest_version = max(versions, key=lambda v: int(v.version))
        logger.info(f"Versão mais recente encontrada: {latest_version.version}")
        
        # Cria diretório model se não existir
        os.makedirs("model", exist_ok=True)
        
        # Baixa o modelo completo
        try:
            model_uri = f"models:/{model_name}/{latest_version.version}"
            logger.info(f"Baixando modelo de: {model_uri}")
            
            # Baixa usando mlflow.sklearn para manter compatibilidade
            model = mlflow.sklearn.load_model(model_uri)
            
            # Salva o modelo localmente usando joblib para compatibilidade
            import joblib
            joblib.dump(model, "model/model.pkl")
            logger.info("Modelo salvo como model.pkl")
            
        except Exception as e:
            logger.warning(f"Erro ao baixar modelo via MLflow, tentando download de artefatos: {e}")
            
            # Fallback: baixa artefatos diretamente
            try:
                download_path = client.download_artifacts(
                    run_id=latest_version.run_id,
                    path="model",
                    dst_path="."
                )
                logger.info(f"Artefatos baixados em: {download_path}")
            except Exception as e2:
                logger.error(f"Falha ao baixar artefatos: {e2}")
                return False
        
        # Busca informações adicionais do run
        run_info = client.get_run(latest_version.run_id)
        metrics = run_info.data.metrics
        
        # Cria metadata do modelo
        model_metadata = {
            "model_name": model_name,
            "version": latest_version.version,
            "run_id": latest_version.run_id,
            "source": latest_version.source,
            "stage": latest_version.current_stage,
            "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": {
                "accuracy": metrics.get("accuracy", "N/A"),
                "f1_score": metrics.get("f1_score", "N/A"),
                "precision": metrics.get("precision", "N/A"),
                "recall": metrics.get("recall", "N/A")
            }
        }
        
        # Salva metadata
        with open("model/model_metadata.json", "w", encoding="utf-8") as f:
            json.dump(model_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info("Metadata do modelo salva com sucesso")
        logger.info(f"Modelo {model_name} v{latest_version.version} baixado com sucesso!")
        logger.info(f"Métricas: Accuracy={metrics.get('accuracy', 'N/A'):.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao baixar modelo: {e}")
        return False

if __name__ == "__main__":
    success = download_latest_model()
    if not success:
        exit(1)
    print("Download concluído com sucesso!")