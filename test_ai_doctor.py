#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script for AI Doctor Gemini integration"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.services import GeminiService

print("\nAI Doctor Integration Test")
print("=" * 60)

# Test if API is configured
is_configured = GeminiService.is_configured()
print("[OK] Gemini API Configured: {}".format(is_configured))

if is_configured:
    print("\n[TEST] Testing with sample symptoms...")
    print("-" * 60)

    symptoms = "I have a persistent headache and mild fever for 2 days"
    result = GeminiService.get_preconsultation_report(symptoms)

    if result.get('error'):
        print("[ERROR] Error: {}".format(result['error']))
        sys.exit(1)
    else:
        print("\n[SUCCESS] Analysis Complete!\n")
        print("[INFO] Urgency Level: {}".format(result.get('urgency')))
        print("[INFO] Recommended Specialist: {}".format(result.get('recommended_specialist')))
        print("[INFO] Reason: {}".format(result.get('specialist_reason')))
        print("\n[INFO] Clinical Summary:")
        print("   {}".format(result.get('summary')))
        print("\n[INFO] Key Symptoms Detected:")
        for symptom in result.get('key_symptoms', []):
            print("   - {}".format(symptom))
        print("\n[INFO] Suggested Tests:")
        for test in result.get('suggested_tests', []):
            print("   - {}".format(test))
        print("\n[INFO] Lifestyle Tips:")
        for tip in result.get('lifestyle_tips', []):
            print("   - {}".format(tip))
        print("\n[INFO] Disclaimer: {}".format(result.get('disclaimer')))
        print("\n" + "=" * 60)
        print("[SUCCESS] AI Doctor integration is working perfectly!")
else:
    print("[ERROR] API not configured - check .env file")
    sys.exit(1)
