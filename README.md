# Financial RAG Application

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-orange.svg)](https://cloud.google.com/vertex-ai)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<div align="center">

### 🌐 Language / Idioma

**[English](#english)** | **[Português](#português)**

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 📋 Overview

A production-ready **Retrieval-Augmented Generation (RAG)** system built with Google's Agent Development Kit (ADK) and FastAPI, designed to help financial professionals analyze invoices and financial documents using AI.

### ✨ Key Features

- 📄 **Document Processing**: Automatic PDF ingestion and vectorization
- 🔍 **Managed RAG**: Fully managed vector storage with Vertex AI RAG Engine
- 🤖 **Intelligent Agent**: Powered by Google ADK with Gemini 1.5 Flash
- 🚀 **FastAPI REST API**: High-performance async endpoints
- ☁️ **Cloud-Native**: Designed for Google Cloud Run with zero-downtime scaling
- 💰 **Cost-Optimized**: Pay-per-use model with scale-to-zero capability

### 🏗️ Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────┐
│   PDF Docs  │───▶│  Vertex AI RAG   │───▶│  Google ADK │───▶│ FastAPI  │
│   (data/)   │    │  Engine (Vector  │    │   (Gemini   │    │   API    │
└─────────────┘    │     Store)       │    │  1.5 Flash) │    └──────────┘
                   └──────────────────┘    └─────────────┘          │
                                                                     ▼
                                                               ┌──────────┐
                                                               │  Client  │
                                                               └──────────┘
```

### 🚀 Quick Start

#### Prerequisites

- Python 3.12 or higher
- Google Cloud Project with Vertex AI API enabled
- Google Cloud CLI installed and configured

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd quantik-ai
```

#### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Google Cloud

```bash
# Authenticate
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

#### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
PROJECT_ID=your-project-id
REGION=us-central1
```

#### 6. Prepare Your Documents

Place your PDF files in the `data/` directory:
```
data/
├── invoice_001.pdf
├── invoice_002.pdf
└── financial_report.pdf
```

#### 7. Create RAG Corpus

Run the automated setup script:
```bash
python prepare_corpus.py
```

This will:
- Create a RAG corpus in Vertex AI
- Upload all PDFs from `data/`
- Update your `.env` with the corpus ID

#### 8. Start the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 📡 API Endpoints

#### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "OK"
}
```

#### Query Documents
```bash
POST /query
Content-Type: application/json

{
  "question": "What is the total amount in invoice 001?"
}
```

**Response:**
```json
{
  "answer": "According to invoice 001, the total amount is $1,234.56..."
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the total amounts in all invoices?"}'
```

### 🐳 Docker Deployment

#### Build Image
```bash
docker build -t financial-rag-api .
```

#### Run Container
```bash
docker run -p 8000:8000 \
  -e PROJECT_ID=your-project-id \
  -e REGION=us-central1 \
  -e RAG_CORPUS=your-corpus-id \
  financial-rag-api
```

### ☁️ Google Cloud Run Deployment

#### 1. Set Environment Variables
```bash
export PROJECT_ID=your-project-id
export REGION=us-central1
export SERVICE_NAME=financial-rag-api
```

#### 2. Build and Push to Container Registry
```bash
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}
```

#### 3. Deploy to Cloud Run
```bash
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION},RAG_CORPUS=${RAG_CORPUS}
```

#### 4. Secure Your Endpoint (Recommended)
```bash
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --no-allow-unauthenticated
```

### 💡 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12+ |
| **Web Framework** | FastAPI |
| **AI Agent** | Google ADK |
| **LLM** | Gemini 1.5 Flash |
| **Vector Store** | Vertex AI RAG Engine |
| **Deployment** | Google Cloud Run |

### 💰 Cost Optimization

- **Vertex AI RAG Engine**: Managed vector storage with pay-per-use pricing
- **Gemini 1.5 Flash**: Most cost-effective Gemini model
- **Cloud Run**: Scales to zero when idle - only pay for active requests
- **No Infrastructure**: Zero server or database management costs

### 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `RAG_CORPUS not set` | Run `python prepare_corpus.py` |
| Import errors | Verify: `pip install -r requirements.txt` |
| Authentication errors | Run: `gcloud auth application-default login` |
| Quota errors | Request quota increases at [GCP Console](https://console.cloud.google.com/iam-admin/quotas) |

### 📁 Project Structure

```
quantik-ai/
├── main.py                    # FastAPI application
├── prepare_corpus.py          # RAG corpus setup script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── .env                       # Environment variables
├── data/                      # PDF documents directory
└── README.md                  # This file
```

### 📝 License

MIT License - feel free to use this project for your own purposes.

---

<a name="português"></a>
## 🇧🇷 Português

### 📋 Visão Geral

Um sistema **RAG (Retrieval-Augmented Generation)** pronto para produção, construído com o Agent Development Kit (ADK) do Google e FastAPI, projetado para ajudar profissionais financeiros a analisar notas fiscais e documentos financeiros usando IA.

### ✨ Funcionalidades Principais

- 📄 **Processamento de Documentos**: Ingestão e vetorização automática de PDFs
- 🔍 **RAG Gerenciado**: Armazenamento vetorial totalmente gerenciado com Vertex AI RAG Engine
- 🤖 **Agente Inteligente**: Alimentado pelo Google ADK com Gemini 1.5 Flash
- 🚀 **API REST FastAPI**: Endpoints assíncronos de alta performance
- ☁️ **Cloud-Native**: Projetado para Google Cloud Run com escalabilidade automática
- 💰 **Otimizado para Custos**: Modelo pay-per-use com capacidade de escalar para zero

### 🏗️ Arquitetura

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────┐
│   PDFs      │───▶│  Vertex AI RAG   │───▶│  Google ADK │───▶│ FastAPI  │
│   (data/)   │    │  Engine (Banco   │    │   (Gemini   │    │   API    │
└─────────────┘    │   Vetorial)      │    │  1.5 Flash) │    └──────────┘
                   └──────────────────┘    └─────────────┘          │
                                                                     ▼
                                                               ┌──────────┐
                                                               │  Cliente │
                                                               └──────────┘
```

### 🚀 Início Rápido

#### Pré-requisitos

- Python 3.12 ou superior
- Projeto Google Cloud com API Vertex AI habilitada
- Google Cloud CLI instalado e configurado

#### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd quantik-ai
```

#### 2. Configure o Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

#### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure o Google Cloud

```bash
# Autenticar
gcloud auth application-default login

# Definir seu projeto
gcloud config set project SEU_PROJECT_ID
```

#### 5. Configure as Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:
```env
PROJECT_ID=seu-project-id
REGION=us-central1
```

#### 6. Prepare Seus Documentos

Coloque seus arquivos PDF no diretório `data/`:
```
data/
├── nota_fiscal_001.pdf
├── nota_fiscal_002.pdf
└── relatorio_financeiro.pdf
```

#### 7. Crie o Corpus RAG

Execute o script de configuração automatizada:
```bash
python prepare_corpus.py
```

Isso irá:
- Criar um corpus RAG no Vertex AI
- Fazer upload de todos os PDFs de `data/`
- Atualizar seu `.env` com o ID do corpus

#### 8. Inicie a Aplicação

```bash
python main.py
```

A API estará disponível em `http://localhost:8000`

### 📡 Endpoints da API

#### Verificação de Saúde
```bash
GET /health
```

**Resposta:**
```json
{
  "status": "OK"
}
```

#### Consultar Documentos
```bash
POST /query
Content-Type: application/json

{
  "question": "Qual é o valor total na nota fiscal 001?"
}
```

**Resposta:**
```json
{
  "answer": "De acordo com a nota fiscal 001, o valor total é R$ 1.234,56..."
}
```

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "Quais são os valores totais de todas as notas fiscais?"}'
```

### 🐳 Deploy com Docker

#### Construir Imagem
```bash
docker build -t financial-rag-api .
```

#### Executar Container
```bash
docker run -p 8000:8000 \
  -e PROJECT_ID=seu-project-id \
  -e REGION=us-central1 \
  -e RAG_CORPUS=seu-corpus-id \
  financial-rag-api
```

### ☁️ Deploy no Google Cloud Run

#### 1. Defina as Variáveis de Ambiente
```bash
export PROJECT_ID=seu-project-id
export REGION=us-central1
export SERVICE_NAME=financial-rag-api
```

#### 2. Construa e Envie para o Container Registry
```bash
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}
```

#### 3. Deploy no Cloud Run
```bash
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION},RAG_CORPUS=${RAG_CORPUS}
```

#### 4. Proteja Seu Endpoint (Recomendado)
```bash
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --no-allow-unauthenticated
```

### 💡 Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Linguagem** | Python 3.12+ |
| **Framework Web** | FastAPI |
| **Agente IA** | Google ADK |
| **LLM** | Gemini 1.5 Flash |
| **Banco Vetorial** | Vertex AI RAG Engine |
| **Deploy** | Google Cloud Run |

### 💰 Otimização de Custos

- **Vertex AI RAG Engine**: Armazenamento vetorial gerenciado com preço pay-per-use
- **Gemini 1.5 Flash**: Modelo Gemini mais econômico
- **Cloud Run**: Escala para zero quando inativo - pague apenas por requisições ativas
- **Sem Infraestrutura**: Zero custos de gerenciamento de servidores ou bancos de dados

### 🔧 Solução de Problemas

| Problema | Solução |
|----------|---------|
| `RAG_CORPUS not set` | Execute `python prepare_corpus.py` |
| Erros de importação | Verifique: `pip install -r requirements.txt` |
| Erros de autenticação | Execute: `gcloud auth application-default login` |
| Erros de quota | Solicite aumento de quota no [Console GCP](https://console.cloud.google.com/iam-admin/quotas) |

### 📁 Estrutura do Projeto

```
quantik-ai/
├── main.py                    # Aplicação FastAPI
├── prepare_corpus.py          # Script de configuração do corpus RAG
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Configuração do container
├── .env                       # Variáveis de ambiente
├── data/                      # Diretório de documentos PDF
└── README.md                  # Este arquivo
```

### 📝 Licença

Licença MIT - sinta-se livre para usar este projeto para seus próprios fins.

---

<div align="center">

**Made with ❤️ using Google Cloud AI**

[⬆ Back to top](#financial-rag-application) | [🇺🇸 English](#english) | [🇧🇷 Português](#português)

</div>
