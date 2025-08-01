#!/usr/bin/env python3
"""
Test setup script to verify environment and dependencies.
Run this before executing the main validation script.
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
        import openai
        print("✓ openai imported successfully")
    except ImportError:
        print("✗ openai not found. Run: pip install openai")
        return False
        
    try:
        import tqdm
        print("✓ tqdm imported successfully")
    except ImportError:
        print("✗ tqdm not found. Run: pip install tqdm")
        return False
    
    return True

def test_api_key():
    """Test if OpenAI API key is set."""
    print("\nTesting API key...")
    
    # Load environment variables from .env file
    load_dotenv()
    
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
        print("✗ API key seems too short (possible error)")
        return False
    
    print("✓ OPENAI_API_KEY is set")
    return True

def test_csv_file():
    """Test if CSV file exists."""
    print("\nTesting CSV file...")
    
    csv_filename = "Mail Order Pharmacies by State Jul 31 2025.csv"
    
    if not os.path.exists(csv_filename):
        print(f"✗ CSV file '{csv_filename}' not found")
        print("Please ensure the CSV file is in the same directory")
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
    print("Pharmacy Validation Setup Test")
    print("=" * 40)
    
    deps_ok = test_dependencies()
    api_ok = test_api_key()
    csv_ok = test_csv_file()
    
    print("\n" + "=" * 40)
    
    if deps_ok and api_ok and csv_ok:
        print("✓ All tests passed! Ready to run validation script.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())