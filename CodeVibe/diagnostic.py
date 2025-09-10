# -*- coding: utf-8 -*-
"""
Quick diagnostic script to test OpenAI library installation
"""
import sys
import os

print("=== OpenAI Library Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

# Test basic import
try:
    import openai
    print(f"✅ OpenAI library found: {openai.__version__}")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")
    sys.exit(1)

# Test OpenAI client import
try:
    from openai import OpenAI
    print("✅ OpenAI client class imported successfully")
except ImportError as e:
    print(f"❌ OpenAI client import failed: {e}")
    sys.exit(1)

# Test SambaCloud-style initialization
try:
    # Use a dummy key for testing
    client = OpenAI(
        api_key="dummy-key-for-testing",
        base_url="https://api.sambanova.ai/v1"
    )
    print("✅ SambaCloud-style client creation successful")
except Exception as e:
    print(f"❌ SambaCloud client creation failed: {e}")

# Test environment variable
samba_key = os.environ.get('SAMBACLOUD_API_KEY')
if samba_key:
    print(f"✅ SAMBACLOUD_API_KEY found (length: {len(samba_key)})")
else:
    print("⚠️ SAMBACLOUD_API_KEY not found in environment")

print("\n=== Testing AI Assistant Import ===")
try:
    from ai_assistant import AIAssistant
    ai = AIAssistant()
    status = ai.get_provider_status()
    print(f"✅ AI Assistant imported successfully")
    print(f"Provider status: {status}")
except Exception as e:
    print(f"❌ AI Assistant import/init failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Diagnostic Complete ===")
