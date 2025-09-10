# -*- coding: utf-8 -*-
"""
Test script to verify AI assistant functionality
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

try:
    print("Testing AI Assistant initialization...")
    
    # Set environment variable if not set
    if 'SAMBACLOUD_API_KEY' not in os.environ:
        os.environ['SAMBACLOUD_API_KEY'] = '9c0f7166-57d0-4f31-97b3-7d8698575065'
    
    from ai_assistant import AIAssistant
    
    # Initialize AI assistant
    ai = AIAssistant()
    
    # Check provider status
    print("\nProvider Status:")
    status = ai.get_provider_status()
    for provider, available in status.items():
        print(f"  {provider}: {'✓ Available' if available else '✗ Not Available'}")
    
    # Get available providers
    available = ai.get_available_providers()
    print(f"\nAvailable Providers: {available}")
    
    # Test a simple response
    print("\nTesting AI response...")
    test_code = "print('Hello, World!')"
    response = ai.get_code_suggestions(test_code)
    print(f"Response: {response[:100]}...")
    
    print("\n✅ AI Assistant test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
