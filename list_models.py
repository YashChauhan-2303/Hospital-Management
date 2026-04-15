#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""List available Gemini models"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

try:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)

    print("\nAvailable Gemini Models for generateContent:")
    print("-" * 60)

    models_found = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            models_found.append(model.name)
            print("  - {}".format(model.name.replace('models/', '')))

    if not models_found:
        print("  No models available - check API key and quota")

    print("-" * 60)
except Exception as e:
    print("Error listing models: {}".format(str(e)))
