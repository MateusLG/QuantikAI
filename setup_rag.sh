#!/bin/bash

# Vertex AI Search Setup Script
# This script creates a data store and uploads documents using gcloud CLI

set -e

# Load configuration from .env
source .env

PROJECT_ID="${PROJECT_ID//\"/}"
REGION="${REGION//\"/}"
DATA_STORE_NAME="${DATA_STORE_NAME:-financial-documents}"
BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-rag-documents}"

echo "================================================================================"
echo "VERTEX AI SEARCH SETUP"
echo "================================================================================"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Data Store: $DATA_STORE_NAME"
echo "Bucket: $BUCKET_NAME"
echo ""

# Step 1: Enable required APIs
echo "Step 1: Enabling required APIs..."
gcloud services enable discoveryengine.googleapis.com --project=$PROJECT_ID
gcloud services enable storage.googleapis.com --project=$PROJECT_ID
echo "✓ APIs enabled"
echo ""

# Step 2: Create GCS bucket
echo "Step 2: Creating GCS bucket..."
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "✓ Bucket already exists: $BUCKET_NAME"
else
    # Extract region prefix (southamerica from southamerica-east1)
    BUCKET_LOCATION=$(echo $REGION | cut -d'-' -f1 | tr '[:lower:]' '[:upper:]')
    if [ "$BUCKET_LOCATION" = "SOUTHAMERICA" ]; then
        BUCKET_LOCATION="SOUTHAMERICA-EAST1"
    fi

    gsutil mb -p $PROJECT_ID -l $BUCKET_LOCATION gs://$BUCKET_NAME
    echo "✓ Bucket created: $BUCKET_NAME"
fi
echo ""

# Step 3: Upload PDFs to GCS
echo "Step 3: Uploading PDFs to GCS..."
PDF_COUNT=$(find data/ -name "*.pdf" -not -name "*:Zone.Identifier" 2>/dev/null | wc -l)

if [ $PDF_COUNT -eq 0 ]; then
    echo "✗ No PDF files found in data/ directory"
    exit 1
fi

echo "  Found $PDF_COUNT PDF file(s)"
gsutil -m cp data/*.pdf gs://$BUCKET_NAME/documents/ 2>/dev/null || true
echo "✓ Documents uploaded"
echo ""

# Step 4: Create data store
echo "Step 4: Creating Vertex AI Search data store..."
echo "  Note: This uses the console UI for now"
echo ""
echo "Please follow these steps:"
echo ""
echo "1. Open: https://console.cloud.google.com/gen-app-builder/engines"
echo "2. Click 'Create App'"
echo "3. Choose 'Search'"
echo "4. Enter app name: $DATA_STORE_NAME"
echo "5. Click 'Continue'"
echo "6. Select 'Cloud Storage'"
echo "7. Enter: gs://$BUCKET_NAME/documents/*.pdf"
echo "8. Click 'Create'"
echo "9. Copy the Data Store ID (format: projects/.../dataStores/...)"
echo ""
echo "Alternatively, use the gcloud alpha command (if available):"
echo ""
echo "gcloud alpha discovery-engine data-stores create $DATA_STORE_NAME \\"
echo "  --project=$PROJECT_ID \\"
echo "  --location=global \\"
echo "  --collection=default_collection \\"
echo "  --industry-vertical=GENERIC \\"
echo "  --solution-types=SOLUTION_TYPE_SEARCH \\"
echo "  --content-config=CONTENT_REQUIRED"
echo ""
echo "================================================================================"
echo ""
read -p "After creating the data store, paste the full Data Store ID here: " DATA_STORE_ID

if [ -z "$DATA_STORE_ID" ]; then
    echo "✗ No Data Store ID provided"
    exit 1
fi

# Step 5: Update .env file
echo ""
echo "Step 5: Updating .env file..."
grep -v "^RAG_CORPUS=" .env > .env.tmp || true
grep -v "^DATA_STORE_NAME=" .env.tmp > .env.tmp2 || true
grep -v "^BUCKET_NAME=" .env.tmp2 > .env.tmp || true
cat .env.tmp > .env
rm -f .env.tmp .env.tmp2

echo "" >> .env
echo "# Vertex AI Search Configuration" >> .env
echo "DATA_STORE_NAME=\"$DATA_STORE_NAME\"" >> .env
echo "BUCKET_NAME=\"$BUCKET_NAME\"" >> .env
echo "RAG_CORPUS=\"$DATA_STORE_ID\"" >> .env

echo "✓ .env file updated"
echo ""
echo "================================================================================"
echo "SETUP COMPLETE!"
echo "================================================================================"
echo ""
echo "Configuration saved to .env:"
echo "  RAG_CORPUS=$DATA_STORE_ID"
echo ""
echo "Next steps:"
echo "  1. Wait a few minutes for documents to be indexed"
echo "  2. Run: python main.py"
echo "  3. Test the API"
echo ""
