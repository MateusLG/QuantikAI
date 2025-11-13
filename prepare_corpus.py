#!/usr/bin/env python3
"""
Vertex AI RAG Corpus Preparation Script

This script automates the creation of a RAG corpus in Vertex AI
and uploads PDF documents from the data/ directory.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import aiplatform
from vertexai.preview import rag

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
CORPUS_DISPLAY_NAME = os.getenv("CORPUS_DISPLAY_NAME", "Financial Documents RAG Corpus")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not PROJECT_ID:
    raise ValueError("PROJECT_ID must be set in .env file")

# Set credentials if provided in .env
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)

print("="*80)
print("VERTEX AI RAG CORPUS SETUP")
print("="*80)
print(f"\nProject ID: {PROJECT_ID}")
print(f"Region: {REGION}")
print(f"Corpus Name: {CORPUS_DISPLAY_NAME}\n")


def create_corpus():
    """Create a new RAG corpus in Vertex AI."""
    print("Step 1: Creating RAG Corpus...")

    try:
        # Create the corpus
        corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            description="Corpus for financial documents and invoices",
        )

        print(f"✓ Corpus created successfully!")
        print(f"  Corpus Name: {corpus.name}")
        print(f"  Display Name: {corpus.display_name}")

        return corpus

    except Exception as e:
        print(f"✗ Error creating corpus: {e}")
        print("\nTroubleshooting:")
        print("  - Ensure Vertex AI API is enabled in your project")
        print("  - Check that you have the necessary IAM permissions")
        print("  - Verify your project ID and region are correct")
        raise


def upload_documents(corpus, data_dir="data"):
    """Upload PDF documents from data directory to the corpus."""
    print("\nStep 2: Uploading Documents...")

    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"✗ Data directory '{data_dir}' not found")
        return []

    pdf_files = list(data_path.glob("*.pdf"))

    if not pdf_files:
        print(f"✗ No PDF files found in '{data_dir}'")
        return []

    print(f"  Found {len(pdf_files)} PDF file(s)")

    uploaded_files = []

    for pdf_file in pdf_files:
        try:
            print(f"\n  Uploading: {pdf_file.name}...")

            # Upload file to corpus
            rag_file = rag.upload_file(
                corpus_name=corpus.name,
                path=str(pdf_file),
                display_name=pdf_file.stem,
                description=f"Financial document: {pdf_file.name}"
            )

            print(f"    ✓ Uploaded successfully")
            print(f"      File Name: {rag_file.name}")
            uploaded_files.append(rag_file)

        except Exception as e:
            print(f"    ✗ Error uploading {pdf_file.name}: {e}")

    return uploaded_files


def update_env_file(corpus):
    """Update .env file with the corpus resource name."""
    print("\nStep 3: Updating .env file...")

    env_path = Path(".env")

    # Read existing .env content
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Remove existing RAG_CORPUS line if present
    lines = [line for line in lines if not line.startswith("RAG_CORPUS=")]

    # Add new RAG_CORPUS
    lines.append(f"\nRAG_CORPUS={corpus.name}\n")

    # Write back to .env
    with open(env_path, "w") as f:
        f.writelines(lines)

    print(f"✓ Updated .env with RAG_CORPUS")
    print(f"  RAG_CORPUS={corpus.name}")


def main():
    try:
        # Step 1: Create corpus
        corpus = create_corpus()

        # Step 2: Upload documents
        uploaded_files = upload_documents(corpus)

        # Step 3: Update .env file
        update_env_file(corpus)

        # Summary
        print("\n" + "="*80)
        print("SETUP COMPLETE!")
        print("="*80)
        print(f"\nCorpus Resource Name:")
        print(f"  {corpus.name}")
        print(f"\nDocuments Uploaded: {len(uploaded_files)}")

        if uploaded_files:
            for rag_file in uploaded_files:
                print(f"  - {rag_file.display_name}")

        print("\nNext Steps:")
        print("  1. Start your application: python main.py")
        print("  2. Query the API: POST http://localhost:8000/query")
        print("\nExample query:")
        print('  curl -X POST http://localhost:8000/query \\')
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"question": "What is the total amount in the invoices?"}\'')
        print()

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
