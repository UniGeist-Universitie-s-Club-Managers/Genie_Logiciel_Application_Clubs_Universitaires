#!/usr/bin/env python
"""
Quick test to verify settings are loading correctly
"""
import os
import sys

# Setup Django  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_project.settings')

import django
django.setup()

from django.conf import settings

print("=" * 70)
print("Django Settings Check")
print("=" * 70)
print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"GOOGLE_API_KEY exists: {bool(settings.GOOGLE_API_KEY)}")
print(f"GOOGLE_API_KEY value: {settings.GOOGLE_API_KEY}")
print(f"GOOGLE_API_KEY length: {len(settings.GOOGLE_API_KEY) if settings.GOOGLE_API_KEY else 0}")
print("=" * 70)
