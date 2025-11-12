# FastAPI RAG Application with Google Cloud Vertex AI

This application provides a Retrieval-Augmented Generation (RAG) system using FastAPI, designed to assist financial professionals. It processes invoices and financial law documents from a specified data source, leveraging Google Cloud Vertex AI for embeddings and generative AI, while focusing on cost-effectiveness.

## Features

*   **Document Ingestion:** Processes PDF documents (invoices, financial laws).
*   **Vector Embeddings:** Utilizes Vertex AI Embeddings API for generating document embeddings.
*   **Retrieval:** Employs a local FAISS vector store for efficient retrieval of relevant document chunks.
*   **Generative AI:** Uses Vertex AI's `gemini-1.0-pro` model for generating answers based on retrieved context.
*   **FastAPI Interface:** Provides a simple REST API for interacting with the RAG system.

## Setup and Installation

### 1. Google Cloud Project Setup

1.  **Create a Google Cloud Project:** If you don't have one, create a new project in the Google Cloud Console.
2.  **Enable APIs:** Enable the following APIs for your project:
    *   Vertex AI API
    *   Cloud Storage API
3.  **Authentication:**
    *   Install the Google Cloud CLI: `gcloud components install gcloud`
    *   Authenticate your local environment: `gcloud auth application-default login`
    *   Ensure your `GOOGLE_CLOUD_PROJECT` environment variable is set to your project ID.

### 2. Local Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Create a Python Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Document Preparation

Place your PDF documents (invoices, financial laws, etc.) into the `data/` directory.

### 4. Configuration

Create a `.env` file in the root directory of the project with the following variables:

```
PROJECT_ID="your-gcp-project-id"
REGION="your-gcp-region" # e.g., us-central1
```

### 5. Running the Application

1.  **Build the Vector Store (Indexing):**
    Before running the API, you need to process your documents and build the vector store. This step will read all PDFs in the `data/` directory, chunk them, create embeddings using Vertex AI, and save the FAISS index locally.

    ```bash
    python main.py index
    ```
    This command will create `faiss_index.bin` and `doc_store.pkl` files in your project root.

2.  **Start the FastAPI Application:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

    The API will be accessible at `http://0.0.0.0:8000`.

## API Endpoints

### `POST /query`

Ask a question to the RAG system.

*   **Request Body:**
    ```json
    {
        "question": "What are the tax implications for a small business in 2025?"
    }
    ```
*   **Response:**
    ```json
    {
        "answer": "According to the documents, the tax implications for a small business in 2025 are..."
    }
    ```

## Deployment to Google Cloud Run (Optional)

For production deployment, you can containerize the application and deploy it to Google Cloud Run.

1.  **Build Docker Image:**
    ```bash
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/rag-app
    ```
2.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy rag-app --image gcr.io/${PROJECT_ID}/rag-app --platform managed --region ${REGION} --allow-unauthenticated --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION}
    ```
    Adjust `--allow-unauthenticated` as per your security requirements.

## Cost Considerations

This application is designed with cost-effectiveness in mind:

*   **Vertex AI Embeddings API:** Pay-per-use for generating embeddings.
*   **Vertex AI `gemini-1.0-pro`:** Pay-per-use for generative AI.
*   **Local FAISS Vector Store:** No direct cost for the vector store itself, only for the compute used during indexing.
*   **Google Cloud Run:** Serverless, scales to zero, meaning you only pay when requests are being processed.

To further minimize costs, ensure you only run the indexing process (`python main.py index`) when documents are updated, and consider setting appropriate concurrency and memory limits for your Cloud Run service.
