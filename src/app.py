"""
API para classificação de Score de Crédito.
Classifica clientes em três categorias: Good, Standard, Poor.
Sistema robusto com fallback local quando MLflow não estiver disponível.
"""

from datetime import datetime
import json
import os
import boto3
import pandas as pd
import numpy as np
from typing import Dict, Any, Union
import logging
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregamento do modelo
model = None
scaler = None
model_info = {}
classes = ["Good", "Standard", "Poor"]

def create_mock_model():
    """Cria um modelo mock para demonstração quando MLflow não está disponível"""
    global model, scaler, model_info
    
    logger.info("Criando modelo mock para demonstração...")
    
    # Modelo mock simples para demonstração
    class MockCreditScoreModel:
        def __init__(self):
            self.classes_ = ["Good", "Standard", "Poor"]
            
        def predict(self, X):
            """Predição baseada em regras simples"""
            predictions = []
            for _, row in X.iterrows():
                # Lógica simples baseada em income e utilização de crédito
                income = row.get('Annual_Income', 0)
                credit_util = row.get('Credit_Utilization_Ratio', 50)
                outstanding_debt = row.get('Outstanding_Debt', 0)
                
                score = 0
                if income > 60000:
                    score += 2
                elif income > 35000:
                    score += 1
                
                if credit_util < 30:
                    score += 2
                elif credit_util < 60:
                    score += 1
                
                if outstanding_debt < 5000:
                    score += 1
                
                # Decidir classificação
                if score >= 4:
                    predictions.append("Good")
                elif score >= 2:
                    predictions.append("Standard")
                else:
                    predictions.append("Poor")
            
            return np.array(predictions)
        
        def predict_proba(self, X):
            """Probabilidades mock"""
            predictions = self.predict(X)
            probabilities = []
            
            for pred in predictions:
                if pred == "Good":
                    probabilities.append([0.05, 0.15, 0.80])  # Poor, Standard, Good
                elif pred == "Standard":
                    probabilities.append([0.20, 0.65, 0.15])
                else:  # Poor
                    probabilities.append([0.75, 0.20, 0.05])
            
            return np.array(probabilities)
    
    model = MockCreditScoreModel()
    model_info = {
        "model_name": "mock_credit_score_model",
        "version": "1.0-demo",
        "type": "mock",
        "description": "Modelo demonstrativo para testes"
    }
    
    logger.info("Modelo mock criado com sucesso!")

def load_model():
    """Carrega modelo com estratégia robusta: MLflow -> Local -> Mock"""
    global model, scaler, model_info
    
    logger.info("Iniciando carregamento do modelo...")
    
    # Verificar se deve forçar o uso do MLflow
    force_mlflow = os.getenv('FORCE_MLFLOW', 'false').lower() == 'true'
    if force_mlflow:
        logger.info(" Apenas MLflow será usado (FORCE_MLFLOW=true)")
    
    # Estratégia 1: Tentar MLflow
    try:
        logger.info("Tentando carregar do MLflow...")
        import mlflow
        import mlflow.pyfunc
        import dagshub
        
        # Configuração MLflow
        dagshub.init(repo_owner="domires", repo_name="fiap-mlops-score-model", mlflow=True)
        mlflow.set_tracking_uri("https://dagshub.com/domires/fiap-mlops-score-model.mlflow")
        
        # Tentar carregar modelo registrado
        try:
            from mlflow.tracking import MlflowClient
            client = MlflowClient()
            model_name = "fiap-mlops-score-model"
            
            registered_versions = client.search_model_versions(f"name='{model_name}'")
            if registered_versions:
                latest_version = max(registered_versions, key=lambda v: int(v.version))
                model_uri = f"models:/{model_name}/{latest_version.version}"
                model = mlflow.pyfunc.load_model(model_uri)
                model_info = {
                    "model_name": model_name,
                    "version": latest_version.version,
                    "run_id": latest_version.run_id,
                    "source": "mlflow_registry"
                }
                logger.info(f"Modelo carregado do MLflow Registry: v{latest_version.version}")
                return
        except Exception as registry_error:
            logger.warning(f"Falha no Model Registry: {registry_error}")
        
        # Tentar runs específicos conhecidos
        run_ids = ["2f5087600685403383420bf1c6720ed5", "bcadaadae75c4ea499bcdad78e9a1d11"]
        for run_id in run_ids:
            try:
                model_uri = f"runs:/{run_id}/model"
                model = mlflow.pyfunc.load_model(model_uri)
                model_info = {
                    "model_name": "fiap-mlops-score-model",
                    "version": "from_run",
                    "run_id": run_id,
                    "source": "mlflow_run"
                }
                logger.info(f"✅ Modelo carregado do MLflow run: {run_id}")
                return
            except Exception as run_error:
                logger.warning(f"Falha no run {run_id}: {run_error}")
                continue
        
    except Exception as mlflow_error:
        logger.warning(f"MLflow não disponível: {mlflow_error}")
        
        # Se modo forçado está ativo, falhar aqui
        if force_mlflow:
            logger.error("ERRO: FORCE_MLFLOW=true mas MLflow não está disponível!")
            logger.error("Verifique: python test_mlflow_connection.py")
            raise Exception(f"MLflow obrigatório mas não disponível: {mlflow_error}")
    
    # Estratégia 2: Modelo local (apenas se não forçar MLflow)
    if not force_mlflow:
        try:
            if os.path.exists('model/model.pkl'):
                import joblib
                model = joblib.load('model/model.pkl')
                
                # Carregar metadata se existir
                if os.path.exists('model/model_metadata.json'):
                    with open('model/model_metadata.json', 'r') as f:
                        model_info = json.load(f)
                        model_info["source"] = "local_file"
                else:
                    model_info = {"model_name": "local_model", "version": "unknown", "source": "local_file"}
                
                logger.info("Modelo local carregado com sucesso!")
                return
        except Exception as local_error:
            logger.warning(f"Falha ao carregar modelo local: {local_error}")
        
        # Estratégia 3: Modelo Mock (sempre funciona, apenas se não forçar MLflow)
        logger.warning("Usando modelo mock para demonstração")
        create_mock_model()
    else:
        # Se chegou aqui no modo forçado, é porque MLflow falhou
        logger.error("ERRO: Não foi possível carregar modelo do MLflow no modo forçado")
        raise Exception("MLflow obrigatório mas modelo não pôde ser carregado")

# Carrega o modelo na inicialização
load_model()

cloudwatch = boto3.client('cloudwatch') if os.getenv('AWS_REGION') else None

def write_real_data(data: Dict[str, Any], prediction: str) -> None:
    """
    Função para escrever os dados consumidos para estudo de data drift.
    
    Args:
        data (dict): dicionário de dados com todas as features de entrada.
        prediction (str): classificação predita (Good, Standard, Poor).
    """
    if not os.getenv('AWS_REGION'):
        logger.info("AWS não configurado, salvando dados localmente")
        return
        
    try:
        now = datetime.now()
        now_formatted = now.strftime("%d-%m-%Y %H:%M")
        file_name = f"{now.strftime('%Y-%m-%d')}_credit_score_prediction_data.csv"
        
        # Adiciona informações da predição
        data_copy = data.copy()
        data_copy["credit_score_prediction"] = prediction
        data_copy["timestamp"] = now_formatted
        data_copy["model_version"] = model_info.get("version", "unknown")
        
        s3 = boto3.client('s3')
        bucket_name = 'fiap-ds-mlops'
        s3_path = 'credit-score-real-data'
        
        try:
            existing_object = s3.get_object(Bucket=bucket_name, Key=f"{s3_path}/{file_name}")
            existing_data = existing_object['Body'].read().decode('utf-8').strip().split('\n')
            existing_data.append(','.join(map(str, data_copy.values())))
            update_content = '\n'.join(existing_data)
        except s3.exceptions.NoSuchKey:
            update_content = ','.join(data_copy.keys()) + '\n' + ','.join(map(str, data_copy.values()))
        
        s3.put_object(Body=update_content, Bucket=bucket_name, Key=f"{s3_path}/{file_name}")
        logger.info(f"Dados salvos em S3: {file_name}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar dados no S3: {e}")

def input_metrics(data: Dict[str, Any], prediction: str, confidence: float = None) -> None:
    """
    Função para escrever métricas customizadas no CloudWatch.
    
    Args:
        data (dict): dicionário de dados com todas as features.
        prediction (str): classificação predita (Good, Standard, Poor).
        confidence (float): confiança da predição (se disponível).
    """
    if not cloudwatch:
        logger.info("CloudWatch não configurado")
        return
        
    try:
        # Métrica principal de classificação
        cloudwatch.put_metric_data(
            MetricData=[
                {
                    'MetricName': 'Credit Score Classification',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': "Classification", 'Value': prediction},
                        {'Name': "ModelVersion", 'Value': str(model_info.get("version", "unknown"))}
                    ]
                },
            ], 
            Namespace='Credit Score Model'
        )
        
        # Métrica de confiança se disponível
        if confidence is not None:
            cloudwatch.put_metric_data(
                MetricData=[
                    {
                        'MetricName': 'Prediction Confidence',
                        'Value': confidence,
                        'Dimensions': [{'Name': "Classification", 'Value': prediction}]
                    },
                ], 
                Namespace='Credit Score Model'
            )
        
        # Métricas de features importantes
        important_features = ['Annual_Income', 'Credit_Utilization_Ratio', 'Payment_Behaviour']
        for feature in important_features:
            if feature in data and data[feature] is not None:
                try:
                    value = float(data[feature])
                    cloudwatch.put_metric_data(
                        MetricData=[
                            {
                                'MetricName': 'Credit Feature Value',
                                'Value': value,
                                'Dimensions': [
                                    {'Name': 'FeatureName', 'Value': feature},
                                    {'Name': 'Classification', 'Value': prediction}
                                ]
                            },
                        ], 
                        Namespace='Credit Score Features'
                    )
                except (ValueError, TypeError):
                    pass
                    
        logger.info(f"Métricas enviadas para CloudWatch: {prediction}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar métricas: {e}")

def validate_and_clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida e limpa os dados de entrada para classificação de credit score.
    """
    # Campos obrigatórios mínimos para funcionar
    core_fields = [
        'Age', 'Annual_Income', 'Monthly_Inhand_Salary', 'Num_Bank_Accounts',
        'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 'Outstanding_Debt',
        'Credit_Utilization_Ratio', 'Total_EMI_per_month', 'Amount_invested_monthly',
        'Monthly_Balance'
    ]
    
    # Campos adicionais para modelos mais complexos
    extended_fields = [
        'Delay_from_due_date', 'Num_of_Delayed_Payment', 'Changed_Credit_Limit',
        'Num_Credit_Inquiries'
    ]
    
    cleaned_data = {}
    
    # Processar campos core (obrigatórios)
    for field in core_fields:
        if field in data:
            try:
                value = data[field]
                if value == "" or value is None:
                    cleaned_data[field] = 0.0
                else:
                    cleaned_data[field] = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Valor inválido para {field}: {data[field]}")
        else:
            # Valor padrão para campos ausentes
            default_values = {
                'Age': 30,
                'Annual_Income': 50000,
                'Monthly_Inhand_Salary': 4000,
                'Num_Bank_Accounts': 2,
                'Num_Credit_Card': 1,
                'Interest_Rate': 15,
                'Num_of_Loan': 1,
                'Outstanding_Debt': 5000,
                'Credit_Utilization_Ratio': 30,
                'Total_EMI_per_month': 500,
                'Amount_invested_monthly': 200,
                'Monthly_Balance': 2000
            }
            cleaned_data[field] = default_values.get(field, 0.0)
    
    # Processar campos extended (opcionais)
    for field in extended_fields:
        if field in data:
            try:
                value = data[field]
                cleaned_data[field] = float(value) if value not in ["", None] else 0.0
            except (ValueError, TypeError):
                cleaned_data[field] = 0.0
        else:
            cleaned_data[field] = 0.0
    
    # Campos categóricos
    categorical_defaults = {
        'Month': 'January',
        'Occupation': 'Engineer',
        'Type_of_Loan': 'Personal Loan',
        'Credit_Mix': 'Standard',
        'Credit_History_Age': '5 Years',
        'Payment_of_Min_Amount': 'Yes',
        'Payment_Behaviour': 'High_spent_Small_value_payments'
    }
    
    for field, default in categorical_defaults.items():
        cleaned_data[field] = data.get(field, default)
    
    # Validações básicas
    if cleaned_data['Age'] < 18 or cleaned_data['Age'] > 100:
        cleaned_data['Age'] = max(18, min(100, cleaned_data['Age']))
    
    if cleaned_data['Annual_Income'] < 0:
        cleaned_data['Annual_Income'] = abs(cleaned_data['Annual_Income'])
        
    if cleaned_data['Credit_Utilization_Ratio'] < 0 or cleaned_data['Credit_Utilization_Ratio'] > 100:
        cleaned_data['Credit_Utilization_Ratio'] = max(0, min(100, cleaned_data['Credit_Utilization_Ratio']))
    
    return cleaned_data

def prepare_model_input(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Prepara os dados para entrada no modelo seguindo o formato usado no treinamento.
    Baseado no arquivo testar_endpoint_mlflow.py da pasta modelo.
    
    Args:
        data (dict): dados validados e limpos.
        
    Returns:
        pd.DataFrame: DataFrame pronto para predição.
    """
    # Features baseadas no arquivo de teste da pasta modelo
    core_features = [
        'Age', 'Annual_Income', 'Monthly_Inhand_Salary', 'Num_Bank_Accounts',
        'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 'Delay_from_due_date',
        'Num_of_Delayed_Payment', 'Changed_Credit_Limit', 'Num_Credit_Inquiries',
        'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Total_EMI_per_month',
        'Amount_invested_monthly', 'Monthly_Balance'
    ]
    
    # Features categóricas opcionais (baseadas no teste do modelo)
    categorical_features = {
        'Month': data.get('Month', 'January'),
        'Occupation': data.get('Occupation', 'Engineer'),
        'Type_of_Loan': data.get('Type_of_Loan', 'Personal Loan'),
        'Credit_Mix': data.get('Credit_Mix', 'Standard'),
        'Credit_History_Age': data.get('Credit_History_Age', '5 Years'),
        'Payment_of_Min_Amount': data.get('Payment_of_Min_Amount', 'Yes'),
        'Payment_Behaviour': data.get('Payment_Behaviour', 'High_spent_Small_value_payments')
    }
    
    # Criar DataFrame com uma linha
    model_data = {}
    
    # Adicionar features numéricas
    for feature in core_features:
        if feature in data:
            model_data[feature] = data[feature]
        else:
            # Mapear nomes alternativos se necessário
            alt_mapping = {
                'Delay_from_due_date': 'Delay_from_due_date',
                'Num_of_Delayed_Payment': 'Num_of_Delayed_Payment',
                'Changed_Credit_Limit': 'Changed_Credit_Limit'
            }
            alt_name = alt_mapping.get(feature, feature)
            model_data[feature] = data.get(alt_name, 0)
    
    # Adicionar features categóricas
    model_data.update(categorical_features)
    
    # Criar DataFrame
    df_input = pd.DataFrame([model_data])
    
    # Garantir tipos corretos para features numéricas
    for col in core_features:
        if col in df_input.columns:
            df_input[col] = pd.to_numeric(df_input[col], errors='coerce').fillna(0)
    
    logger.info(f"DataFrame preparado: {df_input.shape}, Colunas: {list(df_input.columns)}")
    
    return df_input

def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Função principal da API para classificação de Score de Crédito.
    
    Args:
        event (dict): payload de entrada (API Gateway ou Lambda direto).
        context: contexto de execução (opcional).
        
    Returns:
        dict: resposta com classificação e metadados.
    """
    try:
        logger.info(f"Evento recebido: {event}")
        
        # Extração dos dados do evento
        if "body" in event:
            logger.info("Requisição via API Gateway")
            body_str = event.get("body", "{}")
            if isinstance(body_str, str):
                body = json.loads(body_str)
            else:
                body = body_str
            data = body.get("data", {})
        else:
            logger.info("Invocação direta")
            data = event.get("data", {})
        
        if not data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Dados não fornecidos",
                    "message": "Campo 'data' é obrigatório"
                })
            }
        
        # Validação e limpeza dos dados
        try:
            cleaned_data = validate_and_clean_data(data)
            logger.info(f"Dados validados: {list(cleaned_data.keys())}")
        except ValueError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Dados inválidos",
                    "message": str(e)
                })
            }
        
        # Preparação dos dados para o modelo
        try:
            model_input = prepare_model_input(cleaned_data)
            logger.info(f"Input preparado para o modelo: {model_input.shape}")
        except Exception as e:
            logger.error(f"Erro ao preparar input: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Erro no processamento",
                    "message": "Falha na preparação dos dados"
                })
            }
        
        # Predição
        try:
            prediction = model.predict(model_input)[0]
            
            # Calcula probabilidades se disponível
            confidence = None
            probabilities = None
            if hasattr(model, 'predict_proba'):
                try:
                    proba = model.predict_proba(model_input)[0]
                    max_proba_idx = np.argmax(proba)
                    confidence = float(proba[max_proba_idx])
                    
                    # Mapeia classes para probabilidades
                    classes = model.classes_ if hasattr(model, 'classes_') else ['Good', 'Poor', 'Standard']
                    probabilities = {classes[i]: float(proba[i]) for i in range(len(proba))}
                except Exception as e:
                    logger.warning(f"Erro ao calcular probabilidades: {e}")
            
            logger.info(f"Predição: {prediction}, Confiança: {confidence}")
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Erro na predição",
                    "message": "Falha ao executar o modelo"
                })
            }
        
        # Registro de métricas e dados
        try:
            input_metrics(cleaned_data, prediction, confidence)
            write_real_data(cleaned_data, prediction)
        except Exception as e:
            logger.warning(f"Erro ao registrar métricas/dados: {e}")
        
        # Resposta de sucesso
        response_body = {
            "prediction": prediction,
            "model_version": model_info.get("version", "unknown"),
            "model_name": model_info.get("model_name", "fiap-mlops-score-model"),
            "timestamp": datetime.now().isoformat()
        }
        
        if confidence is not None:
            response_body["confidence"] = confidence
        
        if probabilities is not None:
            response_body["probabilities"] = probabilities
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(response_body)
        }
        
    except Exception as e:
        logger.error(f"Erro não tratado: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Erro interno do servidor",
                "message": "Erro inesperado na execução"
            })
        }
