#!/usr/bin/env python3
"""
Test script to verify AI provider functionality.
Run this to test your provider configuration without processing a full CSV.
"""

import os
import sys
from dotenv import load_dotenv
from providers import get_ai_provider

def test_provider():
    """Test the configured AI provider with a sample pharmacy."""
    
    load_dotenv()
    
    # Sample pharmacy data for testing
    test_pharmacy = [{
        'StoreName': 'Test Pharmacy',
        'Address1': '123 Main St',
        'City': 'Anytown',
        'State': 'CA',
        'ZipCode': '90210',
        'Operates in states': 'CA, NV, AZ',
        'NCPDPID': '1234567'
    }]
    
    try:
        # Get configured provider
        ai_provider = get_ai_provider()
        provider_name = os.getenv('AI_PROVIDER', 'openai')
        
        print(f"Testing {provider_name.upper()} provider...")
        print("=" * 50)
        
        # Test validation
        results = ai_provider.validate_batch_with_ai(test_pharmacy)
        
        print("✅ Provider test successful!")
        print(f"Results: {results}")
        
        return True
        
    except Exception as e:
        print(f"❌ Provider test failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your API key is set correctly")
        print("2. Verify your .env file configuration")
        print("3. Make sure dependencies are installed")
        return False

if __name__ == "__main__":
    print("AI Provider Test")
    print("=" * 30)
    
    success = test_provider()
    sys.exit(0 if success else 1)