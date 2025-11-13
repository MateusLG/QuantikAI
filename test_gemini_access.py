#!/usr/bin/env python3
"""
Direct test of Gemini model access
"""

import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

print("=" * 80)
print("GEMINI ACCESS TEST")
print("=" * 80)
print(f"\nProject: {PROJECT_ID}")
print(f"Region: {REGION}")
print()

# Set up environment
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = REGION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

# Test different model names
model_names_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "publishers/google/models/gemini-1.5-flash",
    "publishers/google/models/gemini-1.5-pro",
]

print("Testing different model names:\n")

for model_name in model_names_to_test:
    print(f"Testing: {model_name}")
    try:
        from google.genai import Client

        client = Client(
            vertexai=True,
            project=PROJECT_ID,
            location=REGION
        )

        # Try to generate content
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello, I am working!'",
        )

        print(f"  ✓ SUCCESS! Model is accessible")
        print(f"    Response: {response.text[:100]}")
        print()
        break

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"  ✗ 404 Not Found")
        elif "403" in error_msg:
            print(f"  ✗ 403 Permission Denied")
        elif "429" in error_msg:
            print(f"  ✗ 429 Rate Limit")
        else:
            print(f"  ✗ Error: {error_msg[:100]}")
    print()

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()
print("If all models failed with 404, it means:")
print("  1. Vertex AI Gemini API is not enabled for your project")
print("  2. Your project may not have access to Gemini models")
print()
print("To enable Gemini API access:")
print(f"  1. Visit: https://console.cloud.google.com/vertex-ai/generative/language")
print(f"  2. Make sure you're in project: {PROJECT_ID}")
print(f"  3. Click 'Enable All Recommended APIs'")
print()
print("Or use Cloud Shell:")
print(f"  gcloud config set project {PROJECT_ID}")
print(f"  gcloud services enable aiplatform.googleapis.com")
print(f"  gcloud services enable generativelanguage.googleapis.com")
print()
