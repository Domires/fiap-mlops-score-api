# 🎯 Guia: Como Subir a API com MLflow Obrigatório

Este guia mostra como configurar e executar a API de Credit Score para **buscar dados diretamente do MLflow** ao invés de usar modelos locais ou mock.

## 🚀 Passo a Passo Completo

### 1. **Instalar Dependências Atualizadas**

```bash
# Instalar todas as dependências (incluindo dagshub)
pip install -r requirements.txt
```

### 2. **Testar Conectividade MLflow**

```bash
# Verificar se o MLflow está acessível
python test_mlflow_connection.py
```

**Resultado esperado:**
```
🎉 SUCESSO! MLflow está funcionando
📊 Fonte: registry  
📋 Versão/Run: 2
✅ A API poderá usar modelos do MLflow diretamente!
```

### 3. **Executar API com MLflow Forçado**

```bash
# Subir API garantindo uso do MLflow
python run_api_with_mlflow.py
```

**Resultado esperado:**
```
✅ MLflow está funcionando!
✅ Modelo carregado do MLflow!
📊 Fonte: mlflow_registry
✅ Predição executada com sucesso!
🎉 SUCESSO! API está rodando com MLflow!
```

### 4. **Usar a API**

Após configurado, você pode usar a API normalmente:

```bash
# Demonstração completa
python demo_api.py

# Ou testes
python test.py
```

## 🔧 Como Funciona

### **Modo Normal (padrão)**
A API tenta carregar na ordem:
1. MLflow Registry → 2. MLflow Runs → 3. Arquivo local → 4. Modelo mock

### **Modo MLflow Forçado (FORCE_MLFLOW=true)**
A API tenta carregar na ordem:
1. MLflow Registry → 2. MLflow Runs → ❌ **FALHA se não conseguir**

## 🎛️ Configurações

### **Variável de Ambiente**

```bash
# Forçar uso do MLflow
export FORCE_MLFLOW=true

# Ou no Windows
set FORCE_MLFLOW=true
```

### **Programaticamente**

```python
import os
os.environ['FORCE_MLFLOW'] = 'true'

# Agora importar a API
import sys
sys.path.append('src')
import app
```

## 🔍 Verificações

### **1. Verificar Fonte do Modelo**

```python
import sys
sys.path.append('src')
import app

print(f"Fonte: {app.model_info.get('source')}")
# Deve retornar: 'mlflow_registry' ou 'mlflow_run'
```

### **2. Verificar Conectividade**

```bash
python test_mlflow_connection.py
```

### **3. Verificar Configuração**

```python
import mlflow
print(f"MLflow URI: {mlflow.get_tracking_uri()}")
# Deve retornar: https://dagshub.com/domires/fiap-mlops-score-model.mlflow
```

## ❌ Solução de Problemas

### **Erro: "MLflow não está disponível"**

**Causas possíveis:**
1. Sem conexão com internet
2. DagsHub não acessível
3. Dependências faltando

**Soluções:**
```bash
# 1. Verificar dependências
pip install -r requirements.txt

# 2. Testar conectividade
python test_mlflow_connection.py

# 3. Verificar acesso manual
python -c "import dagshub; print('✅ DagsHub OK')"
```

### **Erro: "Modelo não pôde ser carregado"**

**Causas possíveis:**
1. Modelo não existe no MLflow
2. Credenciais incorretas
3. Versão do modelo incompatível

**Soluções:**
```bash
# 1. Listar modelos disponíveis
python -c "
import mlflow
import dagshub
dagshub.init(repo_owner='domires', repo_name='fiap-mlops-score-model', mlflow=True)
mlflow.set_tracking_uri('https://dagshub.com/domires/fiap-mlops-score-model.mlflow')
from mlflow.tracking import MlflowClient
client = MlflowClient()
models = client.search_model_versions(\"name='fiap-mlops-score-model'\")
for m in models: print(f'Versão: {m.version}, Status: {m.current_stage}')
"
```

### **Erro: "FORCE_MLFLOW=true mas MLflow não está disponível"**

Este é o comportamento esperado quando:
- `FORCE_MLFLOW=true` está configurado
- MLflow não está acessível

**Soluções:**
1. Desativar modo forçado: `export FORCE_MLFLOW=false`
2. Ou corrigir conectividade MLflow

## 🎯 Resumo dos Comandos

```bash
# Configuração inicial
pip install -r requirements.txt

# Testar MLflow
python test_mlflow_connection.py

# Subir API com MLflow obrigatório
python run_api_with_mlflow.py

# Usar API normalmente
python demo_api.py
```

## 📊 Monitoramento

A API logará claramente de onde o modelo foi carregado:

```
✅ Modelo carregado do MLflow Registry: v2
✅ Modelo carregado do MLflow run: 2f50876...
```

**Fontes possíveis:**
- `mlflow_registry`: Modelo do Model Registry
- `mlflow_run`: Modelo de run específico  
- `local_file`: Arquivo local (apenas sem FORCE_MLFLOW)
- `mock`: Modelo demonstrativo (apenas sem FORCE_MLFLOW)