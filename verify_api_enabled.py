#!/usr/bin/env python3
"""
Quick check if Vertex AI Gemini API is enabled
"""

import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = REGION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

print("=" * 80)
print(f"Checking Vertex AI Gemini API for project: {PROJECT_ID}")
print(f"Region: {REGION}")
print("=" * 80)
print()

try:
    from google.genai import Client

    client = Client(
        vertexai=True,
        project=PROJECT_ID,
        location=REGION
    )

    # Try a simple generation
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Reply with just 'API is working'",
    )

    print("✅ SUCCESS! Vertex AI Gemini API is enabled and working!")
    print(f"\nModel response: {response.text}")
    print()
    print("Your FastAPI application should now work.")
    print("Restart it with: python main.py")

except Exception as e:
    error_str = str(e)

    if "404" in error_str:
        print("❌ GEMINI API IS NOT ENABLED")
        print()
        print("The Vertex AI Gemini API is not yet enabled for your project.")
        print()
        print("Please enable it using ONE of these methods:")
        print()
        print("METHOD 1 - Google Cloud Console (Recommended):")
        print("  1. Open this URL in your browser:")
        print(f"     https://console.cloud.google.com/vertex-ai/generative?project={PROJECT_ID}")
        print()
        print("  2. On the 'Generative AI Studio' page, click any model (like Gemini)")
        print("  3. You'll see a button 'Enable All Recommended APIs' - click it")
        print("  4. Wait 1-2 minutes for the API to be enabled")
        print("  5. Run this script again to verify: python verify_api_enabled.py")
        print()
        print("METHOD 2 - Cloud Shell:")
        print("  1. Open Cloud Shell: https://console.cloud.google.com/?cloudshell=true")
        print("  2. Run these commands:")
        print(f"     gcloud config set project {PROJECT_ID}")
        print(f"     gcloud services enable aiplatform.googleapis.com")
        print()
        print("METHOD 3 - Direct API Library Link:")
        print(f"  https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project={PROJECT_ID}")
        print("  Click 'ENABLE'")

    elif "403" in error_str:
        print("❌ PERMISSION DENIED")
        print()
        print("Your account doesn't have permission to use Vertex AI.")
        print("You need one of these roles:")
        print("  - roles/aiplatform.user")
        print("  - roles/ml.developer")
        print("  - roles/owner")

    else:
        print(f"❌ ERROR: {error_str}")

    print()

print("=" * 80)
