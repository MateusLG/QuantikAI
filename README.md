# Financial RAG Application with Google ADK and Vertex AI

This application provides a Retrieval-Augmented Generation (RAG) system using Google's Agent Development Kit (ADK) and FastAPI, designed to assist financial professionals. It processes invoices and financial documents, leveraging Vertex AI RAG Engine for managed retrieval and Gemini for generative AI.

## Features

*   **Document Ingestion:** Processes PDF documents (invoices, financial documents) using Vertex AI RAG Engine.
*   **Managed RAG:** Utilizes Vertex AI RAG Engine for fully managed vector storage and retrieval.
*   **Google ADK Agent:** Powered by Google's Agent Development Kit for intelligent agent orchestration.
*   **Generative AI:** Uses Vertex AI's `gemini-1.5-flash` model for fast, accurate answer generation.
*   **FastAPI Interface:** Provides a simple REST API for interacting with the RAG system.
*   **Cloud-Native:** Designed for deployment on Google Cloud Run with zero local dependencies.

## Setup and Installation

### 1. Google Cloud Project Setup

1.  **Create a Google Cloud Project:** If you don't have one, create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enable APIs:** Enable the following APIs for your project:
    *   Vertex AI API
    *   Cloud Storage API (optional, for document storage)
3.  **Authentication:**
    *   Install the Google Cloud CLI: [Installation Guide](https://cloud.google.com/sdk/docs/install)
    *   Authenticate your local environment:
        ```bash
        gcloud auth application-default login
        ```
    *   Set your project:
        ```bash
        gcloud config set project YOUR_PROJECT_ID
        ```

### 2. Local Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd quantik-ai
    ```

2.  **Create a Python Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Document Preparation

Place your PDF documents (invoices, financial documents, etc.) into the `data/` directory.

Example:
```
data/
├── nf_0001.pdf
├── nf_0002.pdf
└── nf_0003.pdf
```

### 4. Configuration

1.  **Copy the example environment file:**
    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env` and set your Google Cloud configuration:**
    ```env
    PROJECT_ID=your-project-id-here
    REGION=us-central1
    ```

### 5. Setup Vertex AI RAG Corpus

Before running the application, you need to create a RAG corpus and upload your documents to Vertex AI:

**Option 1: Automated Setup (Recommended)**
```bash
python prepare_corpus.py
```

This script will:
- Create a new RAG corpus in Vertex AI
- Upload all PDF files from the `data/` directory
- Automatically update your `.env` file with the corpus ID

**Option 2: Manual Setup**
```bash
python main.py setup
```

This will display instructions for manually creating a corpus via the Google Cloud Console.

### 6. Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be accessible at `http://localhost:8000`.

## API Endpoints

### `GET /health`

Health check endpoint.

*   **Response:**
    ```json
    {
        "status": "OK"
    }
    ```

### `POST /query`

Ask a question to the RAG system.

*   **Request Body:**
    ```json
    {
        "question": "What is the total amount in invoice nf_0001?"
    }
    ```

*   **Response:**
    ```json
    {
        "answer": "According to the invoice nf_0001, the total amount is..."
    }
    ```

*   **Example with curl:**
    ```bash
    curl -X POST http://localhost:8000/query \
         -H "Content-Type: application/json" \
         -d '{"question": "What is the total amount in the invoices?"}'
    ```

## Deployment to Google Cloud Run

For production deployment, containerize the application and deploy it to Google Cloud Run:

1.  **Set environment variables:**
    ```bash
    export PROJECT_ID=your-project-id
    export REGION=us-central1
    export SERVICE_NAME=financial-rag-api
    ```

2.  **Build and push Docker image:**
    ```bash
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}
    ```

3.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy ${SERVICE_NAME} \
        --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION},RAG_CORPUS=${RAG_CORPUS}
    ```

    **Note:** Replace `${RAG_CORPUS}` with your actual corpus resource name from `.env`.

4.  **Secure your endpoint (Recommended):**
    ```bash
    # Remove unauthenticated access
    gcloud run deploy ${SERVICE_NAME} \
        --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --no-allow-unauthenticated
    ```

## Architecture

This application uses:

- **Google ADK (Agent Development Kit):** For intelligent agent orchestration
- **Vertex AI RAG Engine:** Managed vector storage and retrieval
- **Gemini 1.5 Flash:** Fast, cost-effective language model
- **FastAPI:** Modern Python web framework
- **Cloud Run:** Serverless container platform

## Cost Considerations

This application is designed with cost-effectiveness in mind:

*   **Vertex AI RAG Engine:** Managed vector storage with pay-per-use pricing
*   **Vertex AI Embeddings:** Automatic embedding generation (included in RAG Engine)
*   **Gemini 1.5 Flash:** Cost-effective model optimized for speed
*   **Google Cloud Run:** Serverless, scales to zero - only pay when requests are processed

**Cost Optimization Tips:**
- Use Gemini 1.5 Flash instead of Pro for most queries
- Leverage Cloud Run's scale-to-zero capability
- Set appropriate memory and CPU limits
- Monitor usage via Google Cloud Console

## Troubleshooting

### "RAG_CORPUS not set" Error
Run `python prepare_corpus.py` to create and configure your corpus.

### Import Errors
Ensure all dependencies are installed: `pip install -r requirements.txt`

### Authentication Errors
Run `gcloud auth application-default login` and verify your project is set correctly.

### Quota Errors
Request quota increases for:
- Vertex AI API
- Text Embedding API
- Gemini API

Visit: https://console.cloud.google.com/iam-admin/quotas

## Technology Stack

- **Python 3.12+**
- **Google Agent Development Kit (ADK)**
- **FastAPI**
- **Vertex AI RAG Engine**
- **Gemini 1.5 Flash**
- **Google Cloud Run**

## License

[Your License Here]
