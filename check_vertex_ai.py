#!/usr/bin/env python3
"""
Script to check Vertex AI API access and available models
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

print("=" * 80)
print("VERTEX AI ACCESS CHECK")
print("=" * 80)
print(f"\nProject ID: {PROJECT_ID}")
print(f"Region: {REGION}")
print(f"Credentials: {GOOGLE_APPLICATION_CREDENTIALS}")
print()

# Set up environment
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = REGION

# Test 1: Check if credentials file exists
print("Test 1: Checking credentials file...")
if os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    print(f"  ✓ Credentials file exists")
else:
    print(f"  ✗ Credentials file not found")
print()

# Test 2: Try to import and authenticate with google-cloud-aiplatform
print("Test 2: Testing Vertex AI SDK...")
try:
    from google.cloud import aiplatform

    aiplatform.init(project=PROJECT_ID, location=REGION)
    print(f"  ✓ Vertex AI SDK initialized")
    print(f"    Project: {aiplatform.constants.base.DEFAULT_PROJECT}")
    print(f"    Location: {aiplatform.constants.base.DEFAULT_LOCATION}")
except Exception as e:
    print(f"  ✗ Error: {e}")
print()

# Test 3: Try listing models
print("Test 3: Listing available models...")
try:
    from google.cloud import aiplatform

    models = aiplatform.Model.list(
        filter='display_name="gemini*"',
        order_by="create_time desc"
    )

    if models:
        print(f"  Found {len(models)} Gemini models:")
        for model in models[:5]:
            print(f"    - {model.display_name} ({model.resource_name})")
    else:
        print("  No Gemini models found")
except Exception as e:
    print(f"  ✗ Error: {e}")
    print(f"    This likely means Vertex AI API is not enabled")
print()

# Test 4: Try using google-genai SDK directly
print("Test 4: Testing google-genai SDK...")
try:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

    from google.genai import Client

    client = Client(
        vertexai=True,
        project=PROJECT_ID,
        location=REGION
    )

    # Try to list models
    models = client.models.list()
    print(f"  ✓ Connected to Vertex AI via google-genai SDK")
    print(f"  Available models:")
    for model in list(models)[:10]:
        print(f"    - {model.name}")

except Exception as e:
    print(f"  ✗ Error: {e}")
print()

# Test 5: Check if we can access the ServiceUsage API to check enabled services
print("Test 5: Checking enabled APIs...")
try:
    from google.cloud import serviceusage_v1

    client = serviceusage_v1.ServiceUsageClient()
    parent = f"projects/{PROJECT_ID}"

    # Check specific APIs
    apis_to_check = [
        "aiplatform.googleapis.com",
        "generativelanguage.googleapis.com",
        "discoveryengine.googleapis.com"
    ]

    for api in apis_to_check:
        try:
            service_name = f"{parent}/services/{api}"
            service = client.get_service(name=service_name)
            status = "ENABLED" if service.state == serviceusage_v1.State.ENABLED else "DISABLED"
            print(f"  {api}: {status}")
        except Exception as e:
            print(f"  {api}: ERROR - {e}")

except Exception as e:
    print(f"  ✗ Error checking APIs: {e}")
print()

print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()
print("If APIs are not enabled, run these commands in Google Cloud Shell:")
print(f"  gcloud config set project {PROJECT_ID}")
print(f"  gcloud services enable aiplatform.googleapis.com")
print(f"  gcloud services enable generativelanguage.googleapis.com")
print()
print("Or enable via Console:")
print(f"  https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project={PROJECT_ID}")
print()
