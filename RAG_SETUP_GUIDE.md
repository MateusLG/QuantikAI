# Guia de Configuração do RAG com Vertex AI Search

## Problema Resolvido

O erro `ModuleNotFoundError: No module named 'google.adk.tools.vertexai_tools'` foi corrigido. O código agora usa a importação correta:

```python
from google.adk.tools import VertexAiSearchTool
```

## Configurações Realizadas

### 1. ✅ Credenciais Configuradas

Arquivo `.env` atualizado com:
```bash
PROJECT_ID="gen-lang-client-0260265792"
REGION="southamerica-east1"
GOOGLE_APPLICATION_CREDENTIALS="/home/mateus/.config/gcloud/application_default_credentials.json"
```

### 2. ✅ Código Corrigido

`main.py` atualizado para usar:
- `VertexAiSearchTool` em vez de `VertexAiRagRetrieval`
- Parâmetro `data_store_id` em vez de `rag_corpora`

## Opções para Configurar o RAG

### Opção 1: Script Python Automatizado (Recomendado)

Use o novo script que criei:

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Executar o script
python prepare_corpus_new.py
```

Este script:
- Cria um bucket no Google Cloud Storage
- Faz upload dos PDFs da pasta `data/`
- Cria um Data Store no Vertex AI Search
- Importa os documentos
- Atualiza automaticamente o `.env`

### Opção 2: Script Shell com gcloud

```bash
# Tornar o script executável
chmod +x setup_rag.sh

# Executar
./setup_rag.sh
```

Este script:
- Habilita as APIs necessárias
- Cria o bucket GCS
- Faz upload dos arquivos
- Fornece instruções para criar o data store via console

### Opção 3: Manual via Console do Google Cloud

1. **Criar bucket no GCS:**
   - Acesse: https://console.cloud.google.com/storage
   - Crie um bucket (ex: `gen-lang-client-0260265792-rag-documents`)
   - Região: South America (São Paulo)
   - Faça upload dos PDFs da pasta `data/`

2. **Criar Data Store no Vertex AI Search:**
   - Acesse: https://console.cloud.google.com/gen-app-builder/engines
   - Clique em "Create App"
   - Escolha "Search"
   - Configure:
     - Nome: `financial-documents`
     - Tipo: Generic
     - Fonte de dados: Cloud Storage
     - Caminho: `gs://seu-bucket/documents/*.pdf`
   - Copie o Data Store ID (formato: `projects/.../dataStores/...`)

3. **Atualizar `.env`:**
   ```bash
   RAG_CORPUS="projects/123456789/locations/global/collections/default_collection/dataStores/financial-documents_xxx"
   ```

## Verificação

Teste se está funcionando:

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Iniciar a aplicação
python main.py

# Em outro terminal, teste a API
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total amount in the invoices?"}'
```

## Estrutura de Arquivos

```
quantik-ai/
├── data/                       # PDFs para indexar
│   ├── nf_0001.pdf
│   ├── nf_0002.pdf
│   └── nf_0003.pdf
├── main.py                     # Aplicação principal (CORRIGIDO)
├── prepare_corpus.py           # Script antigo (não funciona)
├── prepare_corpus_new.py       # Script novo com Vertex AI Search
├── setup_rag.sh               # Script shell alternativo
├── .env                        # Configurações (ATUALIZADO)
└── RAG_SETUP_GUIDE.md         # Este guia
```

## Troubleshooting

### Erro: "Permission denied"
```bash
# Verificar autenticação
gcloud auth list

# Se necessário, fazer login novamente
gcloud auth application-default login
```

### Erro: "API not enabled"
```bash
# Habilitar APIs necessárias
gcloud services enable discoveryengine.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

### Erro: "Region not supported"
```bash
# Vertex AI Search usa location "global", não regional
# Certifique-se de usar "global" ao criar o data store
```

### Script trava sem output
- Verifique se as credenciais estão corretas
- Confirme que as APIs estão habilitadas
- Tente usar o método manual via console

## Próximos Passos

Depois que o RAG corpus estiver configurado:

1. ✅ Inicie a aplicação: `python main.py`
2. ✅ Teste endpoints:
   - Health check: `GET http://localhost:8000/health`
   - Query: `POST http://localhost:8000/query`
3. ✅ Monitore logs para ver as interações

## Recursos Úteis

- [Vertex AI Search Documentation](https://cloud.google.com/generative-ai-app-builder/docs)
- [Google ADK Documentation](https://github.com/google/adk-python)
- [VertexAiSearchTool Reference](https://github.com/google/adk-python/tree/main/src/google/adk/tools)
