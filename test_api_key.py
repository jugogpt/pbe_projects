"""
Test script to verify OpenAI API key is loaded correctly
"""

import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("OpenAI API Key Test")
print("=" * 60)
print()

# Load environment variables
print("1. Loading .env file...")
load_dotenv()
print("   [OK] .env file loaded")
print()

# Check if API key exists
api_key = os.getenv("OPENAI_API_KEY")
print("2. Checking OPENAI_API_KEY...")
if api_key:
    print(f"   [OK] API key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"   [OK] Key length: {len(api_key)} characters")
else:
    print("   [ERROR] API key NOT found!")
    print()
    print("   Please check:")
    print("   - .env file exists in project root")
    print("   - OPENAI_API_KEY line is present")
    print("   - No extra spaces or quotes around the key")
    print()
    exit(1)

print()

# Test OpenAI import
print("3. Testing OpenAI package...")
try:
    from openai import OpenAI
    print("   [OK] OpenAI package imported successfully")
except ImportError as e:
    print(f"   [ERROR] Failed to import OpenAI: {e}")
    print("   Run: pip install openai")
    exit(1)

print()

# Test OpenAI client initialization
print("4. Testing OpenAI client initialization...")
try:
    client = OpenAI(api_key=api_key)
    print("   [OK] OpenAI client created successfully")
except Exception as e:
    print(f"   [ERROR] Failed to create OpenAI client: {e}")
    exit(1)

print()

# Test a simple API call (list models - doesn't cost anything)
print("5. Testing API connection (listing models)...")
try:
    models = client.models.list()
    print("   [OK] Successfully connected to OpenAI API")
    print(f"   [OK] Found {len(models.data)} available models")
except Exception as e:
    print(f"   [ERROR] API call failed: {e}")
    print()
    print("   Common issues:")
    print("   - Invalid API key")
    print("   - No internet connection")
    print("   - OpenAI service is down")
    print("   - Account has no credits")
    exit(1)

print()
print("=" * 60)
print("[SUCCESS] All tests passed! Voice assistant should work.")
print("=" * 60)
print()
print("You can now run: python main.py")
