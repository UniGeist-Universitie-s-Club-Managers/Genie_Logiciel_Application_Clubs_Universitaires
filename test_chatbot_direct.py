#!/usr/bin/env python
"""
Direct test of the chatbot view function
"""
import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_project.settings')
django.setup()

from accounts.views import chatbot_view
from accounts.models import User

print("=" * 60)
print("Direct Chatbot View Test")
print("=" * 60)

# Create a mock request
factory = RequestFactory()
request = factory.get('/accounts/chatbot/')

# Try with anonymous user first
request.user = AnonymousUser()
print("Testing with anonymous user...")
try:
    response = chatbot_view(request)
    print(f"Response status: {response.status_code}")
    if hasattr(response, 'content'):
        content = response.content.decode()
        if "non configurée" in content:
            print("✗ Found 'non configurée' error with anonymous user")
        else:
            print("✓ No API key error with anonymous user")
except Exception as e:
    print(f"Exception with anonymous user: {e}")

# Try with a logged-in user
print("\nTesting with logged-in user...")
try:
    user = User.objects.filter(is_active=True).first()
    if user:
        request.user = user
        response = chatbot_view(request)
        print(f"Response status: {response.status_code}")
        if hasattr(response, 'content'):
            content = response.content.decode()
            if "non configurée" in content:
                print("✗ Found 'non configurée' error with logged-in user")
            else:
                print("✓ No API key error with logged-in user")
        else:
            print("Response has no content attribute")
    else:
        print("No active users found in database")
except Exception as e:
    print(f"Exception with logged-in user: {e}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
