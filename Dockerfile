# API de Classificação de Score de Crédito
FROM public.ecr.aws/lambda/python:3.11

# Metadados da imagem
LABEL maintainer="FIAP MLOps Team"
LABEL description="API for Credit Score Classification using MLflow"
LABEL version="1.0.0"

# Configuração do ambiente
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}
ENV PYTHONUNBUFFERED=1

# Copia arquivo de dependências
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY model_downloader.py ${LAMBDA_TASK_ROOT}/

# Cria diretório para modelos
RUN mkdir -p ${LAMBDA_TASK_ROOT}/model

# Copia arquivos de modelo se existirem (opcional)
COPY model/ ${LAMBDA_TASK_ROOT}/model/ 2>/dev/null || true

# Copia dados de exemplo para testes
COPY data.json ${LAMBDA_TASK_ROOT}/
COPY test.py ${LAMBDA_TASK_ROOT}/

# Arquivo de entrada principal
COPY src/app.py ${LAMBDA_TASK_ROOT}/

# Configurações de saúde
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import src.app; print('API Health: OK')" || exit 1

# Define o handler principal
CMD [ "app.handler" ]