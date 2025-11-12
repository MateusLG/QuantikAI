import os
import pickle
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import ChatVertexAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

if not PROJECT_ID or not REGION:
    raise ValueError("PROJECT_ID and REGION environment variables must be set.")

app = FastAPI()

# --- RAG Components ---
vectorstore = None
llm = None
qa_chain = None

def initialize_rag_components():
    global vectorstore, llm, qa_chain

    if vectorstore is None:
        try:
            # Load the FAISS index and document store
            embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001", project=PROJECT_ID, location=REGION)
            vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            with open("doc_store.pkl", "rb") as f:
                vectorstore.docstore = pickle.load(f)
            print("FAISS index and document store loaded successfully.")
        except Exception as e:
            print(f"Could not load FAISS index or document store: {e}")
            vectorstore = None # Ensure it's None if loading fails

    if llm is None:
        llm = ChatVertexAI(model_name="gemini-1.0-pro", project=PROJECT_ID, location=REGION)
        print("Vertex AI LLM initialized.")

    if vectorstore and llm and qa_chain is None:
        prompt_template = """
        You are a financial assistant. Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer as concise as possible.

        {context}

        Question: {question}
        Helpful Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": PROMPT}
        )
        print("QA Chain initialized.")

# --- Indexing Function ---
def index_documents():
    print("Starting document indexing...")
    data_path = "data/"
    documents = []
    for file_name in os.listdir(data_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(data_path, file_name)
            print(f"Loading {file_path}...")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        print("No PDF documents found in the 'data/' directory. Exiting indexing.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(texts)} text chunks.")

    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001", project=PROJECT_ID, location=REGION)
    print("Generating embeddings and building FAISS index...")
    global vectorstore
    vectorstore = FAISS.from_documents(texts, embeddings)
    vectorstore.save_local("faiss_index")
    with open("doc_store.pkl", "wb") as f:
        pickle.dump(vectorstore.docstore, f)
    print("FAISS index and document store saved successfully.")

# --- FastAPI Models ---
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# --- FastAPI Endpoints ---
@app.on_event("startup")
async def startup_event():
    # Initialize RAG components on startup if not in indexing mode
    if os.environ.get("INDEXING_MODE") != "true":
        initialize_rag_components()

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    if qa_chain is None:
        raise HTTPException(status_code=503, detail="RAG components not initialized. Please run indexing first.")
    
    try:
        result = qa_chain.invoke({"query": request.question})
        return QueryResponse(answer=result["result"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {e}")

# --- Command Line Interface for Indexing ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        os.environ["INDEXING_MODE"] = "true" # Set flag to prevent RAG component initialization during indexing
        index_documents()
        print("Indexing complete. You can now run the FastAPI application.")
    else:
        # This block will run when `uvicorn main:app` is executed
        # Uvicorn handles the startup event, which calls initialize_rag_components
        uvicorn.run(app, host="0.0.0.0", port=8000)
