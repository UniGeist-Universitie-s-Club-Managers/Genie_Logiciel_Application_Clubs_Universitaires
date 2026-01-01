#!/usr/bin/env python
"""
Test script to access the chatbot endpoint and check for errors
"""
import os
import sys
import requests
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_project.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()

print("=" * 70)
print("Testing Chatbot Endpoint")
print("=" * 70)

# Get or create a test user
try:
    user = User.objects.get(username='admin')
    print(f"✓ Using existing user: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_superuser(username='admin', email='admin@test.com', password='admin123')
    print(f"✓ Created test user: {user.username}")

# Create a client and login
client = Client()
is_logged_in = client.login(username='admin', password='admin123')
print(f"✓ Logged in: {is_logged_in}")

# Access the chatbot page
chatbot_url = reverse('accounts:chatbot')
print(f"\nAccessing chatbot at: {chatbot_url}")

response = client.get(chatbot_url)
print(f"Response status: {response.status_code}")

if response.status_code == 200:
    print("✓ Chatbot page loaded successfully")
    
    # Check if the error message is in the response
    if "non configurée" in response.content.decode():
        print("✗ ERROR: Found 'non configurée' message in response")
        # Print relevant parts
        lines = response.content.decode().split('\n')
        for i, line in enumerate(lines):
            if 'non configurée' in line:
                print(f"  Line {i}: {line.strip()}")
    else:
        print("✓ No 'non configurée' error message found")
else:
    print(f"✗ ERROR: Status code {response.status_code}")

print("\n" + "=" * 70)
print("Test complete")
print("=" * 70)
