# API de Classificação de Score de Crédito

Esta API classifica clientes em categorias de score de crédito baseada em suas características financeiras e comportamentais.

## 📋 Funcionalidades

- **Classificação de Score**: Classifica em Good, Standard ou Poor
- **Validação de Dados**: Validação robusta dos dados de entrada
- **MLflow Integration**: Carrega modelos diretamente do MLflow
- **Monitoramento**: Métricas CloudWatch e logging detalhado
- **Data Drift**: Coleta dados para análise de drift

## 🚀 Quick Start

### 1. Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Baixar o modelo mais recente
python model_downloader.py
```

### 2. Execução Local

```bash
# Executar teste
python test.py

# Ou executar testes com pytest
pytest test.py -v
```

### 3. Deploy com Docker

```bash
# Build da imagem
docker build -t credit-score-api .

# Executar container
docker run -p 8080:8080 credit-score-api
```

## 📊 API Reference

### Endpoint Principal

**POST** `/predict` (ou invocação direta da função)

### Request Format

```json
{
  "data": {
    "Age": 35,
    "Annual_Income": 50000,
    "Monthly_Inhand_Salary": 4166.67,
    "Num_Bank_Accounts": 2,
    "Num_Credit_Card": 3,
    "Interest_Rate": 12.5,
    "Num_of_Loan": 2,
    "Outstanding_Debt": 15000,
    "Credit_Utilization_Ratio": 25.5,
    "Total_EMI_per_month": 800,
    "Amount_invested_monthly": 500,
    "Monthly_Balance": 2500,
    "Occupation": "Engineer",
    "Credit_Mix": "Good",
    "Payment_of_Min_Amount": "No",
    "Payment_Behaviour": "Low_spent_Medium_value_payments"
  }
}
```

### Response Format

```json
{
  "prediction": "Good",
  "confidence": 0.85,
  "probabilities": {
    "Good": 0.85,
    "Standard": 0.12,
    "Poor": 0.03
  },
  "model_version": "1.0.0",
  "model_name": "fiap-mlops-score-model",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 📝 Campos de Entrada

### Campos Obrigatórios (Numéricos)

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `Age` | float | Idade do cliente (18-100) | 35 |
| `Annual_Income` | float | Renda anual em USD | 50000 |
| `Monthly_Inhand_Salary` | float | Salário líquido mensal | 4166.67 |
| `Num_Bank_Accounts` | int | Número de contas bancárias | 2 |
| `Num_Credit_Card` | int | Número de cartões de crédito | 3 |
| `Interest_Rate` | float | Taxa de juros (%) | 12.5 |
| `Num_of_Loan` | int | Número de empréstimos | 2 |
| `Outstanding_Debt` | float | Dívida pendente em USD | 15000 |
| `Credit_Utilization_Ratio` | float | Taxa de utilização de crédito (%) | 25.5 |
| `Total_EMI_per_month` | float | Total de EMIs mensais | 800 |
| `Amount_invested_monthly` | float | Valor investido mensalmente | 500 |
| `Monthly_Balance` | float | Saldo mensal médio | 2500 |

### Campos Opcionais (Categóricos)

| Campo | Tipo | Valores Aceitos | Padrão |
|-------|------|-----------------|--------|
| `Occupation` | string | Qualquer profissão | "Other" |
| `Credit_Mix` | string | Good, Standard, Poor | "Standard" |
| `Payment_of_Min_Amount` | string | Yes, No | "No" |
| `Payment_Behaviour` | string | Padrões de pagamento | "Low_spent_Medium_value_payments" |

## 🔧 Respostas de Erro

### 400 - Bad Request
```json
{
  "error": "Dados inválidos",
  "message": "Idade deve estar entre 18 e 100 anos"
}
```

### 500 - Internal Server Error
```json
{
  "error": "Erro na predição",
  "message": "Falha ao executar o modelo"
}
```

## 🧪 Testando a API

### Exemplo com curl

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @data.json \
  http://localhost:8080/predict
```

### Exemplo com Python

```python
import requests
import json

# Dados de exemplo
data = {
    "data": {
        "Age": 35,
        "Annual_Income": 50000,
        # ... outros campos
    }
}

response = requests.post(
    "http://localhost:8080/predict",
    json=data
)

result = response.json()
print(f"Score de Crédito: {result['prediction']}")
```

## 📈 Monitoramento

### CloudWatch Metrics

- `Credit Score Classification`: Contagem por classificação
- `Prediction Confidence`: Confiança das predições
- `Credit Feature Value`: Valores das features importantes

### Logs

- Informações de cada predição
- Erros e warnings detalhados
- Tempo de resposta e performance

## 🔒 Segurança

### Funcionalidades Implementadas

- Validação rigorosa de entrada
- Tratamento de exceções
- Logging de segurança
- Headers CORS configurados

### Para Produção (TODO)

- [ ] Autenticação JWT
- [ ] Rate limiting/throttling
- [ ] Validação de API Key
- [ ] Audit logs

## 🐳 Docker

### Build

```bash
docker build -t credit-score-api .
```

### Run

```bash
docker run -p 8080:8080 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  credit-score-api
```

## 📋 Estrutura do Projeto

```
api/
├── src/
│   └── app.py              # Código principal da API
├── model/                  # Modelos baixados (criado automaticamente)
├── tests/                  # Testes automatizados
├── data.json              # Dados de exemplo
├── test.py                # Testes principais
├── model_downloader.py    # Script para baixar modelo
├── requirements.txt       # Dependências
├── Dockerfile            # Container configuration
└── README.md             # Esta documentação
```

## 🔄 Workflow

1. **Treinamento**: Modelo treinado no MLflow
2. **Download**: `model_downloader.py` baixa última versão
3. **API**: Serve predições via `app.py`
4. **Monitoramento**: Dados coletados para drift analysis
5. **Retreino**: Cycle continua baseado em performance

## 🤝 Contribuição

1. Fork o repositório
2. Crie sua feature branch
3. Adicione testes para novas funcionalidades
4. Execute os testes existentes
5. Submeta um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique logs da aplicação
- Execute os testes: `python test.py`
- Verifique conectividade com MLflow
- Consulte documentação do MLflow