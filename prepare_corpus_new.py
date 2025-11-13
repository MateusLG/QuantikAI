#!/usr/bin/env python3
"""
Vertex AI Search Data Store Preparation Script

This script creates a Vertex AI Search data store and uploads documents.
Compatible with Google ADK's VertexAiSearchTool.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import storage
from google.api_core import operation
import time

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "southamerica-east1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DATA_STORE_NAME = os.getenv("DATA_STORE_NAME", "financial-documents")
BUCKET_NAME = os.getenv("BUCKET_NAME", f"{PROJECT_ID}-rag-documents")

if not PROJECT_ID:
    raise ValueError("PROJECT_ID must be set in .env file")

# Set credentials if provided in .env
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

print("="*80)
print("VERTEX AI SEARCH DATA STORE SETUP")
print("="*80)
print(f"\nProject ID: {PROJECT_ID}")
print(f"Region: {REGION}")
print(f"Data Store Name: {DATA_STORE_NAME}")
print(f"Bucket Name: {BUCKET_NAME}\n")


def create_gcs_bucket():
    """Create a Google Cloud Storage bucket for documents."""
    print("Step 1: Creating GCS Bucket...")

    try:
        storage_client = storage.Client(project=PROJECT_ID)

        # Check if bucket already exists
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
            print(f"✓ Bucket already exists: {BUCKET_NAME}")
            return bucket
        except Exception:
            pass

        # Create new bucket
        bucket = storage_client.create_bucket(
            BUCKET_NAME,
            location=REGION.split("-")[0].upper()  # Convert southamerica-east1 to SOUTHAMERICA
        )

        print(f"✓ Bucket created successfully: {BUCKET_NAME}")
        return bucket

    except Exception as e:
        print(f"✗ Error creating bucket: {e}")
        print("\nTroubleshooting:")
        print("  - Ensure Cloud Storage API is enabled")
        print("  - Check that you have storage.buckets.create permission")
        print("  - Try a different bucket name if it's already taken globally")
        raise


def upload_pdfs_to_gcs(bucket):
    """Upload PDF files from data/ directory to GCS."""
    print("\nStep 2: Uploading PDFs to GCS...")

    data_path = Path("data")
    if not data_path.exists():
        print(f"✗ Data directory 'data/' not found")
        return []

    pdf_files = list(data_path.glob("*.pdf"))

    if not pdf_files:
        print(f"✗ No PDF files found in 'data/'")
        return []

    print(f"  Found {len(pdf_files)} PDF file(s)")

    uploaded_uris = []

    for pdf_file in pdf_files:
        try:
            # Skip Zone.Identifier files
            if ":Zone.Identifier" in str(pdf_file):
                continue

            blob_name = f"documents/{pdf_file.name}"
            blob = bucket.blob(blob_name)

            print(f"\n  Uploading: {pdf_file.name}...")
            blob.upload_from_filename(str(pdf_file))

            uri = f"gs://{BUCKET_NAME}/{blob_name}"
            print(f"    ✓ Uploaded to: {uri}")
            uploaded_uris.append(uri)

        except Exception as e:
            print(f"    ✗ Error uploading {pdf_file.name}: {e}")

    return uploaded_uris


def create_data_store():
    """Create a Vertex AI Search data store."""
    print("\nStep 3: Creating Vertex AI Search Data Store...")

    try:
        # Use global location for Discovery Engine
        location = "global"

        client = discoveryengine.DataStoreServiceClient()

        # Check if data store already exists
        parent = f"projects/{PROJECT_ID}/locations/{location}/collections/default_collection"

        try:
            data_store_path = f"{parent}/dataStores/{DATA_STORE_NAME}"
            existing_store = client.get_data_store(name=data_store_path)
            print(f"✓ Data store already exists: {existing_store.name}")
            return existing_store
        except Exception:
            pass

        # Create new data store
        data_store = discoveryengine.DataStore(
            display_name=DATA_STORE_NAME,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        )

        request = discoveryengine.CreateDataStoreRequest(
            parent=parent,
            data_store=data_store,
            data_store_id=DATA_STORE_NAME,
        )

        op = client.create_data_store(request=request)
        print("  Waiting for data store creation (this may take a few minutes)...")

        response = op.result(timeout=300)

        print(f"✓ Data store created successfully!")
        print(f"  Name: {response.name}")
        print(f"  Display Name: {response.display_name}")

        return response

    except Exception as e:
        print(f"✗ Error creating data store: {e}")
        print("\nTroubleshooting:")
        print("  - Ensure Discovery Engine API is enabled:")
        print("    gcloud services enable discoveryengine.googleapis.com")
        print("  - Check IAM permissions for Discovery Engine")
        print(f"  - Verify project ID: {PROJECT_ID}")
        raise


def import_documents_to_datastore(data_store, gcs_uris):
    """Import documents from GCS to the data store."""
    print("\nStep 4: Importing Documents to Data Store...")

    if not gcs_uris:
        print("  No documents to import")
        return

    try:
        client = discoveryengine.DocumentServiceClient()

        # Prepare import request
        gcs_source = discoveryengine.GcsSource(
            input_uris=gcs_uris,
            data_schema="content"
        )

        request = discoveryengine.ImportDocumentsRequest(
            parent=f"{data_store.name}/branches/default_branch",
            gcs_source=gcs_source,
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )

        print(f"  Importing {len(gcs_uris)} document(s)...")
        op = client.import_documents(request=request)

        print("  Waiting for import to complete (this may take several minutes)...")
        response = op.result(timeout=600)

        print(f"✓ Documents imported successfully!")
        print(f"  Imported: {len(gcs_uris)} document(s)")

        return response

    except Exception as e:
        print(f"✗ Error importing documents: {e}")
        print("\nNote: Document import may continue in the background.")
        print("Check the console for status.")
        raise


def update_env_file(data_store):
    """Update .env file with the data store ID."""
    print("\nStep 5: Updating .env file...")

    env_path = Path(".env")

    # Read existing .env content
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Remove existing RAG_CORPUS line if present
    lines = [line for line in lines if not line.startswith("RAG_CORPUS=")]
    lines = [line for line in lines if not line.startswith("DATA_STORE_NAME=")]
    lines = [line for line in lines if not line.startswith("BUCKET_NAME=")]

    # Add configuration
    lines.append(f"\n# Vertex AI Search Configuration\n")
    lines.append(f"DATA_STORE_NAME={DATA_STORE_NAME}\n")
    lines.append(f"BUCKET_NAME={BUCKET_NAME}\n")
    lines.append(f"RAG_CORPUS={data_store.name}\n")

    # Write back to .env
    with open(env_path, "w") as f:
        f.writelines(lines)

    print(f"✓ Updated .env file")
    print(f"  RAG_CORPUS={data_store.name}")


def main():
    try:
        # Step 1: Create GCS bucket
        bucket = create_gcs_bucket()

        # Step 2: Upload PDFs to GCS
        gcs_uris = upload_pdfs_to_gcs(bucket)

        # Step 3: Create data store
        data_store = create_data_store()

        # Step 4: Import documents
        if gcs_uris:
            import_documents_to_datastore(data_store, gcs_uris)

        # Step 5: Update .env file
        update_env_file(data_store)

        # Summary
        print("\n" + "="*80)
        print("SETUP COMPLETE!")
        print("="*80)
        print(f"\nData Store ID:")
        print(f"  {data_store.name}")
        print(f"\nGCS Bucket:")
        print(f"  gs://{BUCKET_NAME}/")
        print(f"\nDocuments: {len(gcs_uris)}")

        print("\nNext Steps:")
        print("  1. Wait a few minutes for indexing to complete")
        print("  2. Start your application: python main.py")
        print("  3. Query the API: POST http://localhost:8000/query")
        print("\nExample query:")
        print('  curl -X POST http://localhost:8000/query \\')
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"question": "What is the total amount in the invoices?"}\'')
        print()

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nFor more help, check:")
        print("  - https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
