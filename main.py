import os
import uvicorn
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# --- Environment and Configuration ---
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
RAG_CORPUS = os.getenv("RAG_CORPUS")

if not PROJECT_ID:
    raise ValueError("PROJECT_ID environment variable must be set in a .env file.")

print(f"GCP Project ID: {PROJECT_ID}")
print(f"GCP Region: {REGION}")

# Google ADK imports
from google.adk.agents import LlmAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- FastAPI Application ---
app = FastAPI(title="Financial RAG API")

# --- RAG Components (Global Variables) ---
rag_agent: Optional[LlmAgent] = None
rag_runner: Optional[Runner] = None
session_service: Optional[InMemorySessionService] = None

# --- RAG Initialization ---
def initialize_rag_components():
    global rag_agent, rag_runner, session_service
    print("\n--- Initializing RAG Agent with Google ADK... ---")

    if not RAG_CORPUS:
        print("Warning: RAG_CORPUS not set. Please run the corpus preparation script first.")
        print("The agent will still be created but retrieval may not work until corpus is configured.")

    try:
        # Set up environment variables for ADK authentication
        os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
        os.environ["GOOGLE_CLOUD_LOCATION"] = REGION
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

        # Create LLM Agent (basic version without RAG for now)
        rag_agent = LlmAgent(
            model="gemini-1.5-flash",
            name="financial_assistant",
            instruction="""You are a financial assistant that helps users understand financial documents and invoices.

Provide helpful and accurate answers to questions about financial documents.
If you don't know the answer, just say that you don't know.
Keep your answers concise and accurate."""
        )

        # Create session service and runner
        session_service = InMemorySessionService()
        rag_runner = Runner(
            app_name="financial_rag_api",
            agent=rag_agent,
            session_service=session_service
        )

        print("--- RAG Agent initialized successfully with Gemini 1.5 Flash and Vertex AI RAG Engine. ---")

    except Exception as e:
        print(f"Error initializing RAG Agent: {e}")
        raise

# --- Corpus Setup Function ---
def setup_corpus():
    """
    This function provides instructions for setting up Vertex AI RAG corpus.
    For actual corpus creation and document upload, use the prepare_corpus.py script.
    """
    print("\n" + "="*80)
    print("VERTEX AI RAG CORPUS SETUP")
    print("="*80)
    print("\nTo use this RAG application, you need to:")
    print("\n1. Create a RAG corpus in Vertex AI")
    print("2. Upload your PDF documents to the corpus")
    print("3. Add the corpus ID to your .env file")
    print("\nUse the prepare_corpus.py script to automate this process:")
    print("\n  python prepare_corpus.py")
    print("\nOr manually via Google Cloud Console:")
    print(f"\n  - Navigate to: https://console.cloud.google.com/gen-app-builder/engines")
    print(f"  - Project: {PROJECT_ID}")
    print(f"  - Region: {REGION}")
    print("  - Create a new RAG API corpus")
    print("  - Upload PDFs from the 'data/' directory")
    print("  - Copy the corpus resource name to .env as RAG_CORPUS")
    print("\nCorpus resource name format:")
    print("  projects/<project-number>/locations/<region>/ragCorpora/<corpus-id>")
    print("\n" + "="*80)

    # Check for PDFs in data directory
    data_path = "data/"
    if os.path.exists(data_path):
        pdf_files = [f for f in os.listdir(data_path) if f.endswith(".pdf")]
        if pdf_files:
            print(f"\nFound {len(pdf_files)} PDF file(s) in '{data_path}':")
            for pdf in pdf_files:
                print(f"  - {pdf}")
        else:
            print(f"\nWarning: No PDF files found in '{data_path}'")
    else:
        print(f"\nWarning: '{data_path}' directory not found")
    print()

# --- FastAPI Models ---
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# --- FastAPI Endpoints ---
@app.on_event("startup")
async def startup_event():
    if os.environ.get("INDEXING_MODE") != "true":
        initialize_rag_components()

@app.get("/health", summary="Health Check")
async def health_check():
    """Returns a 200 OK response if the server is running."""
    return {"status": "OK"}

@app.post("/query", response_model=QueryResponse, summary="Query the RAG System")
async def query_rag(request: QueryRequest):
    """
    Receives a question, retrieves relevant context from the document corpus,
    and generates an answer using the RAG agent powered by Google ADK.
    """
    if rag_runner is None or session_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG agent is not initialized. Please ensure the server has started correctly."
        )

    print(f"Received query: {request.question}")
    try:
        # Use a consistent user_id and create a new session for each query
        import uuid
        user_id = "api_user"
        session_id = str(uuid.uuid4())

        # Create the session
        await session_service.create_session(
            app_name="financial_rag_api",
            user_id=user_id,
            session_id=session_id
        )

        # Create message content
        message = types.Content(
            role="user",
            parts=[types.Part(text=request.question)]
        )

        # Run the agent asynchronously
        answer_parts = []
        async for event in rag_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            # Extract text from agent responses
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        answer_parts.append(part.text)

        # Combine all answer parts
        answer = " ".join(answer_parts) if answer_parts else "No response generated."

        print(f"Generated answer: {answer}")
        return QueryResponse(answer=answer)

    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the query: {e}"
        )

# --- Command Line Interface ---
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_corpus()
    else:
        print("Starting FastAPI server...")
        print("Use 'python main.py setup' to see corpus setup instructions")
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
