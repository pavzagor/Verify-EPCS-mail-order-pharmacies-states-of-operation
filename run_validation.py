#!/usr/bin/env python3
"""
Simple runner script for pharmacy validation.
This script handles the complete workflow with error checking.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Failed to run command: {str(e)}")
        return False

def main():
    """Main execution workflow."""
    print("Pharmacy States of Operation Validation")
    print("=" * 50)
    
    # Check if API key is set
    load_dotenv()  # Load .env file if it exists
    
    # Check if appropriate API key is set based on provider
    ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
    
    if ai_provider == 'openai' and not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set!")
        print("\nPlease set your OpenAI API key using one of these methods:")
        print("1. Environment variable: export OPENAI_API_KEY='your-key-here'")
        print("2. Create .env file with: OPENAI_API_KEY=your-key-here")
        print("\nThen run this script again.")
        return 1
    elif ai_provider == 'google' and not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not set!")
        print("\nPlease set your Google API key using one of these methods:")
        print("1. Environment variable: export GOOGLE_API_KEY='your-key-here'")
        print("2. Create .env file with: GOOGLE_API_KEY=your-key-here")
        print("3. Get your API key from: https://aistudio.google.com/app/apikey")
        print("\nThen run this script again.")
        return 1
    
    # Install dependencies
    print("Installing dependencies...")
    
    # Try UV first (if available), then fall back to pip
    uv_success = run_command("uv sync", "Installing requirements with UV")
    if not uv_success:
        print("UV not available, trying pip...")
        if not run_command("pip install -r requirements.txt", "Installing requirements with pip"):
            print("Failed to install dependencies. Please install manually:")
            print("With UV: uv sync")
            print("With pip: pip install openai google-genai pandas tqdm python-dotenv")
            return 1
    
    # Run setup test
    print("\nRunning setup verification...")
    if not run_command("python test_setup.py", "Testing setup"):
        print("Setup test failed. Please check the errors above.")
        return 1
    
    # Run validation
    print("\nStarting validation process...")
    print("This may take several minutes depending on your dataset size.")
    
    if not run_command("python validate_pharmacy_states.py", "Running validation"):
        print("Validation failed. Check the log files for details.")
        return 1
    
    print("\n" + "=" * 50)
    print("✅ Validation completed successfully!")
    print("Check the output CSV file and log files for results.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())