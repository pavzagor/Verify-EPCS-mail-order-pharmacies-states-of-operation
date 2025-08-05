#!/usr/bin/env python3
"""
Test setup script to verify environment and dependencies.
Run this before executing the main validation script.
Supports both OpenAI and Google Gemini providers.
"""

import sys
import os
from dotenv import load_dotenv

def test_dependencies():
    """Test if all required dependencies are installed."""
    print("Testing dependencies...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError:
        print("✗ pandas not found. Run: pip install pandas")
        return False
        
    try:
        import tqdm
        print("✓ tqdm imported successfully")
    except ImportError:
        print("✗ tqdm not found. Run: pip install tqdm")
        return False
    
    # Test AI provider-specific dependencies
    load_dotenv()
    ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
    
    if ai_provider == 'openai':
        try:
            import openai
            print("✓ openai imported successfully")
        except ImportError:
            print("✗ openai not found. Run: pip install openai")
            return False
    
    elif ai_provider == 'google':
        try:
            from google import genai
            print("✓ google-genai imported successfully")
        except ImportError:
            print("✗ google-genai not found. Run: pip install google-genai")
            return False
    
    return True

def test_api_key():
    """Test if AI provider API key is set."""
    print("\nTesting API configuration...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
    print(f"✓ AI Provider: {ai_provider}")
    
    if ai_provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            env_file_exists = os.path.exists('.env')
            print("✗ OPENAI_API_KEY not found")
            print("Please set it using one of these methods:")
            print("1. Environment variable: export OPENAI_API_KEY='your-key-here'")
            print("2. Create .env file with: OPENAI_API_KEY=your-key-here")
            if env_file_exists:
                print("   (.env file exists but doesn't contain OPENAI_API_KEY)")
            return False
        
        if len(api_key) < 20:
            print("✗ OpenAI API key seems too short (possible error)")
            return False
        
        print("✓ OPENAI_API_KEY is set")
        
        # Check model configuration
        model = os.getenv('OPENAI_MODEL', 'o3-deep-research')
        print(f"✓ Configured model: {model}")
        
        if model == 'o3-deep-research':
            print("⚠️  Note: o3-deep-research requires Verified Organization status")
            print("   If you get access errors, try setting OPENAI_MODEL=gpt-4o in .env")
    
    elif ai_provider == 'google':
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            env_file_exists = os.path.exists('.env')
            print("✗ GOOGLE_API_KEY not found")
            print("Please set it using one of these methods:")
            print("1. Environment variable: export GOOGLE_API_KEY='your-key-here'")
            print("2. Create .env file with: GOOGLE_API_KEY=your-key-here")
            print("3. Get your API key from: https://aistudio.google.com/app/apikey")
            if env_file_exists:
                print("   (.env file exists but doesn't contain GOOGLE_API_KEY)")
            return False
        
        if len(api_key) < 20:
            print("✗ Google API key seems too short (possible error)")
            return False
        
        print("✓ GOOGLE_API_KEY is set")
        
        # Check model configuration
        model = os.getenv('GOOGLE_MODEL', 'gemini-2.5-pro')
        print(f"✓ Configured model: {model}")
        
        # Check Google-specific features
        search_grounding = os.getenv('ENABLE_SEARCH_GROUNDING', 'true').lower() == 'true'
        url_grounding = os.getenv('ENABLE_URL_GROUNDING', 'true').lower() == 'true'
        print(f"✓ Search grounding: {search_grounding}")
        print(f"✓ URL grounding: {url_grounding}")
    
    else:
        print(f"✗ Unknown AI provider: {ai_provider}")
        print("Supported providers: 'openai', 'google'")
        return False
    
    return True

def test_csv_file():
    """Test if CSV file exists."""
    print("\nTesting CSV file...")
    
    # Load environment variables to get CSV configuration
    load_dotenv()
    csv_directory = os.getenv('CSV_DIRECTORY', 'CSVs')
    csv_filename = os.path.join(csv_directory, os.getenv('CSV_FILENAME', 'Mail order active EPCS pharmacies w states - Master 31 Jul 2025.csv'))
    
    if not os.path.exists(csv_filename):
        print(f"✗ CSV file '{csv_filename}' not found")
        print(f"Expected directory: {csv_directory}")
        print("Please ensure the CSV file exists in the specified location.")
        print("You can configure the CSV location in .env file:")
        print("  CSV_DIRECTORY=your-directory")
        print("  CSV_FILENAME=your-filename.csv")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_filename)
        print(f"✓ CSV file loaded successfully ({len(df)} rows)")
        
        if 'Operates in states' not in df.columns:
            print("✗ Required column 'Operates in states' not found")
            print(f"Available columns: {list(df.columns)}")
            return False
        
        print("✓ Required column 'Operates in states' found")
        return True
        
    except Exception as e:
        print(f"✗ Error reading CSV: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Pharmacy Validation Setup Test (Multi-Provider)")
    print("=" * 50)
    
    deps_ok = test_dependencies()
    api_ok = test_api_key()
    csv_ok = test_csv_file()
    
    print("\n" + "=" * 50)
    
    if deps_ok and api_ok and csv_ok:
        print("✓ All tests passed! Ready to run validation script.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())