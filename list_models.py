#!/usr/bin/env python
"""
List available Gemini models
"""
import os
import sys
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_project.settings')

import django
django.setup()

from django.conf import settings

api_key = getattr(settings, 'GOOGLE_API_KEY', None)

print("Listing available Gemini models...")
print("=" * 60)

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    models = genai.list_models()
    for model in models:
        print(f"Model: {model.name}")
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✓ Supports generateContent")
        print()
except Exception as e:
    print(f"Error: {str(e)}")
