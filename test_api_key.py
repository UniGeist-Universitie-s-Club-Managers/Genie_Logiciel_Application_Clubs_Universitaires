#!/usr/bin/env python
"""
Test script to verify that GOOGLE_API_KEY is loaded correctly from .env
"""
import os
import sys
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_project.settings')

import django
django.setup()

from django.conf import settings

print("=" * 60)
print("Testing GOOGLE_API_KEY loading...")
print("=" * 60)

api_key = getattr(settings, 'GOOGLE_API_KEY', None)

if api_key:
    print("✓ API Key loaded successfully!")
    print(f"  Key (first 20 chars): {api_key[:20]}...")
    print(f"  Full key length: {len(api_key)} characters")
else:
    print("✗ ERROR: API Key is None or not configured!")
    print(f"  Check that .env file exists at: {Path.cwd() / '.env'}")
    sys.exit(1)

# Test Gemini connection
print("\nTesting Gemini API connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say 'Hello World'")
    print("✓ Gemini API connection successful!")
    print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ ERROR: Failed to connect to Gemini API: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! API is working correctly.")
print("=" * 60)
