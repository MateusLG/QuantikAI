import os
import pickle
import uvicorn
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# --- Environment and Configuration ---
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

if not PROJECT_ID or not REGION:
    raise ValueError("PROJECT_ID and REGION environment variables must be set in a .env file.")

print(f"GCP Project ID: {PROJECT_ID}")
print(f"GCP Region: {REGION}")

# --- Langchain Imports ---
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_google_vertexai import VertexAIEmbeddings
    from langchain_google_vertexai import ChatVertexAI
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    print("All langchain modules imported successfully.")
except ImportError as e:
    print(f"Error importing langchain modules: {e}")
    sys.exit(1)

# --- FastAPI Application ---
app = FastAPI(title="Financial RAG API")

# --- RAG Components (Global Variables) ---
vectorstore = None
rag_chain = None

# --- RAG Initialization ---
def initialize_rag_components():
    global vectorstore, rag_chain
    print("\n--- Initializing RAG components... ---")

    # 1. Initialize Embeddings Model
    try:
        embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001", project=PROJECT_ID, location=REGION)
        print("Vertex AI Embeddings initialized successfully.")
    except Exception as e:
        print(f"Error initializing Vertex AI Embeddings: {e}")
        return

    # 2. Load FAISS Vector Store
    if vectorstore is None:
        try:
            vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            with open("doc_store.pkl", "rb") as f:
                vectorstore.docstore = pickle.load(f)
            print("FAISS index and document store loaded successfully.")
        except Exception as e:
            print(f"Could not load FAISS index. Please run indexing first: `python main.py index`. Error: {e}")
            vectorstore = None
            return

    # 3. Initialize LLM
    try:
        llm = ChatVertexAI(model_name="gemini-1.0-pro", project=PROJECT_ID, location=REGION)
        print("Vertex AI LLM initialized successfully.")
    except Exception as e:
        print(f"Error initializing Vertex AI LLM: {e}")
        return

    # 4. Create RAG Chain
    if vectorstore and llm and rag_chain is None:
        print("Creating RAG chain...")
        system_prompt = """
        You are a financial assistant. Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer as concise as possible.

        {context}
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(vectorstore.as_retriever(), question_answer_chain)
        print("--- RAG components initialized successfully. ---")

# --- Indexing Function ---
def index_documents():
    print("\n--- Starting document indexing... ---")
    data_path = "data/"
    
    # 1. Load Documents
    documents = []
    for file_name in os.listdir(data_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(data_path, file_name)
            print(f"Loading document: {file_path}")
            try:
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    if not documents:
        print("No PDF documents found in 'data/' directory. Exiting indexing.")
        return

    # 2. Split Documents
    print(f"Loaded {len(documents)} document pages. Splitting into text chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} text chunks.")

    # 3. Generate Embeddings and Create FAISS Index
    print("Initializing embeddings model for indexing...")
    try:
        embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001", project=PROJECT_ID, location=REGION)
        print("Generating embeddings and building FAISS index...")
        global vectorstore
        vectorstore = FAISS.from_documents(texts, embeddings)
        
        # 4. Save FAISS Index
        print("Saving FAISS index and document store...")
        vectorstore.save_local("faiss_index")
        with open("doc_store.pkl", "wb") as f:
            pickle.dump(vectorstore.docstore, f)
        print("--- Indexing complete. FAISS index saved to 'faiss_index'. ---")
    except Exception as e:
        print(f"An error occurred during embedding and indexing: {e}")

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
    Receives a question, retrieves relevant context from the document store,
    and generates an answer using a large language model.
    """
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG chain is not initialized. Please ensure indexing is complete and the server has started correctly.")
    
    print(f"Received query: {request.question}")
    try:
        result = rag_chain.invoke({"input": request.question})
        print(f"Generated answer: {result['answer']}")
        return QueryResponse(answer=result["answer"])
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the query: {e}")

# --- Command Line Interface ---
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        os.environ["INDEXING_MODE"] = "true"
        index_documents()
    else:
        print("Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
