#!/usr/bin/env python3
"""
Pharmacy States of Operation Validation Script

This script validates pharmacy states of operation using multiple AI providers:
- OpenAI (o3-deepresearch, o4-mini-deep-research, gpt-4o, etc.)
- Google Gemini (gemini-2.5-pro with search and URL grounding)

It processes a CSV file in batches and adds validation results to new columns.

Requirements:
    pip install openai google-genai pandas tqdm

Usage:
    1. Set your API key(s) as environment variables or in .env file
    2. Configure AI_PROVIDER in .env (openai or google)
    3. Place your CSV file in the same directory as this script
    4. Update CSV_FILENAME if your file has a different name
    5. Run: python validate_pharmacy_states.py

Author: Generated for MEDvidi Pharmacy Verification
"""

import pandas as pd
import os
import sys
import time
from typing import List, Dict, Any
from tqdm import tqdm
import logging
from datetime import datetime
from dotenv import load_dotenv
from providers import get_ai_provider

# Load environment variables first
load_dotenv()

# Configuration
CSV_DIRECTORY = os.getenv('CSV_DIRECTORY', 'CSVs')
CSV_FILENAME = os.path.join(CSV_DIRECTORY, os.getenv('CSV_FILENAME', 'Mail order active EPCS pharmacies w states - Master 31 Jul 2025.csv'))
OUTPUT_FILENAME = f"validated_pharmacies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '30'))
RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', '2'))  # seconds between API calls

# AI Provider Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai').lower()  # 'openai' or 'google'

# Model Configuration - Set your preferred model per provider
# OpenAI Models:
# - o3-deep-research: Best quality with web search, requires Verified Organization ($10-40/1M + $10/1K searches)  
# - o4-mini-deep-research: Cheaper deep research option ($2-8/1M + $10/1K searches)
# - gpt-4o: Good alternative, more accessible ($5-15/1M + $25/1K searches)
# Google Models:
# - gemini-2.5-pro: Advanced reasoning with search grounding
# - gemini-2.5-flash: Fast and cost-effective

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'validation_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PharmacyStateValidator:
    def __init__(self):
        """Initialize the validator with the configured AI provider."""
        self.setup_ai_provider()
        
    def setup_ai_provider(self):
        """Set up AI provider based on configuration."""
        try:
            self.ai_provider = get_ai_provider(AI_PROVIDER)
            logger.info(f"AI provider '{AI_PROVIDER}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI provider '{AI_PROVIDER}': {str(e)}")
            sys.exit(1)

    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load and validate CSV file."""
        try:
            df = pd.read_csv(filename)
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            
            # Check if required column exists
            if 'Operates in states' not in df.columns:
                logger.error("'Operates in states' column not found in CSV!")
                logger.error(f"Available columns: {list(df.columns)}")
                sys.exit(1)
                
            return df
        except FileNotFoundError:
            logger.error(f"CSV file '{filename}' not found!")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            sys.exit(1)

    def validate_batch_with_ai(self, batch: List[Dict]) -> List[Dict]:
        """Validate a batch of pharmacies using the configured AI provider."""
        return self.ai_provider.validate_batch_with_ai(batch)

    def process_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the entire CSV in batches, saving after each successful batch."""
        
        # Add new columns
        df['Initial states of operation correct'] = None
        df[f'States of operation by {AI_PROVIDER.upper()} AI'] = ""
        df['Validation confidence'] = ""
        df['Validation reasoning'] = ""
        
        # Process in batches
        total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE
        logger.info(f"Processing {len(df)} pharmacies in {total_batches} batches of {BATCH_SIZE}")
        
        for batch_idx in tqdm(range(0, len(df), BATCH_SIZE), desc="Processing batches"):
            batch_end = min(batch_idx + BATCH_SIZE, len(df))
            batch_df = df.iloc[batch_idx:batch_end].copy()
            
            # Convert batch to list of dictionaries
            batch_pharmacies = batch_df.to_dict('records')
            
            # Validate with AI provider
            validations = self.validate_batch_with_ai(batch_pharmacies)
            
            # Apply results back to dataframe
            batch_successful = False
            for validation in validations:
                try:
                    pharmacy_idx = validation.get('pharmacy_index', 1) - 1  # Convert to 0-based
                    actual_idx = batch_idx + pharmacy_idx
                    
                    if actual_idx < len(df):
                        df.loc[actual_idx, 'Initial states of operation correct'] = validation.get('is_correct')
                        df.loc[actual_idx, f'States of operation by {AI_PROVIDER.upper()} AI'] = validation.get('corrected_states', '')
                        df.loc[actual_idx, 'Validation confidence'] = validation.get('confidence', '')
                        df.loc[actual_idx, 'Validation reasoning'] = validation.get('reasoning', '')
                        batch_successful = True
                        
                except Exception as e:
                    logger.error(f"Error applying validation result: {str(e)}")
                    continue
            
            # Save progress after each successful batch
            if batch_successful:
                try:
                    df.to_csv(OUTPUT_FILENAME, index=False)
                    logger.info(f"Progress saved: Batch {batch_idx//BATCH_SIZE + 1}/{total_batches} completed")
                except Exception as e:
                    logger.error(f"Error saving progress: {str(e)}")
            
            # Rate limiting
            if batch_idx + BATCH_SIZE < len(df):  # Don't delay after the last batch
                logger.info(f"Waiting {RATE_LIMIT_DELAY} seconds before next batch...")
                time.sleep(RATE_LIMIT_DELAY)
        
        return df

    def save_results(self, df: pd.DataFrame, output_filename: str):
        """Save the validated results to a new CSV file."""
        try:
            df.to_csv(output_filename, index=False)
            logger.info(f"Results saved to: {output_filename}")
            
            # Print summary statistics
            total_pharmacies = len(df)
            correct_count = len(df[df['Initial states of operation correct'] == True])
            incorrect_count = len(df[df['Initial states of operation correct'] == False])
            error_count = len(df[df['Initial states of operation correct'].isna()])
            
            logger.info(f"\nValidation Summary (AI Provider: {AI_PROVIDER}):")
            logger.info(f"Total pharmacies: {total_pharmacies}")
            logger.info(f"Correct states of operation: {correct_count}")
            logger.info(f"Incorrect states of operation: {incorrect_count}")
            logger.info(f"Validation errors: {error_count}")
            logger.info(f"Success rate: {((correct_count + incorrect_count) / total_pharmacies * 100):.1f}%")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            sys.exit(1)


def main():
    """Main execution function."""
    logger.info("Starting Pharmacy States of Operation Validation")
    logger.info("=" * 50)
    
    # Load environment variables first
    load_dotenv()
    logger.info("Environment variables loaded from .env file (if present)")
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILENAME):
        logger.error(f"CSV file '{CSV_FILENAME}' not found!")
        logger.error(f"Please ensure the CSV file exists in the specified location.")
        logger.error(f"Expected directory: {CSV_DIRECTORY}")
        logger.error(f"You can configure the CSV location in .env file:")
        logger.error(f"  CSV_DIRECTORY=your-directory")
        logger.error(f"  CSV_FILENAME=your-filename.csv")
        sys.exit(1)
    
    # Initialize validator
    validator = PharmacyStateValidator()
    
    # Load CSV
    df = validator.load_csv(CSV_FILENAME)
    
    # Process CSV (saves progress after each successful batch)
    validated_df = validator.process_csv(df)
    
    # Final save and summary
    validator.save_results(validated_df, OUTPUT_FILENAME)
    
    logger.info("Validation completed successfully!")
    logger.info(f"Check the output file: {OUTPUT_FILENAME}")


if __name__ == "__main__":
    main()