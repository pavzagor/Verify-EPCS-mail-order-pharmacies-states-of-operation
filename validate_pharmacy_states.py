#!/usr/bin/env python3
"""
Pharmacy States of Operation Validation Script

This script validates pharmacy states of operation using OpenAI's o3-deepresearch API.
It processes a CSV file in batches and adds validation results to new columns.

Requirements:
    pip install openai pandas tqdm

Usage:
    1. Set your OpenAI API key as environment variable: export OPENAI_API_KEY="your-key-here"
    2. Place your CSV file in the same directory as this script
    3. Update CSV_FILENAME if your file has a different name
    4. Run: python validate_pharmacy_states.py

Author: Generated for MEDvidi Pharmacy Verification
"""

import pandas as pd
import openai
import os
import sys
import time
from typing import List, Dict, Any
import json
from tqdm import tqdm
import logging
from datetime import datetime

# Configuration
CSV_FILENAME = "Mail Order Pharmacies by State Jul 31 2025.csv"
OUTPUT_FILENAME = f"validated_pharmacies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
BATCH_SIZE = 30
RATE_LIMIT_DELAY = 2  # seconds between API calls

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
        """Initialize the validator with OpenAI client."""
        self.setup_openai()
        
    def setup_openai(self):
        """Set up OpenAI client with API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set!")
            logger.error("Please set it with: export OPENAI_API_KEY='your-key-here'")
            sys.exit(1)
        
        self.client = openai.OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully")

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

    def create_validation_prompt(self, pharmacies_batch: List[Dict]) -> str:
        """Create a prompt for OpenAI to validate pharmacy states of operation."""
        
        prompt = """You are a healthcare regulatory expert specializing in pharmacy licensing and operations across U.S. states. 

Your task is to verify if the listed "states of operation" for each mail-order pharmacy are accurate based on current regulatory information, licensing requirements, and known operational status.

For each pharmacy, analyze:
1. Current licensing status in claimed states
2. Regulatory compliance for mail-order operations
3. Any known restrictions or suspensions
4. Cross-reference with known pharmacy chains and their actual operational scope

IMPORTANT: Base your analysis on factual regulatory information, not assumptions.

Pharmacies to validate:
"""
        
        for i, pharmacy in enumerate(pharmacies_batch, 1):
            prompt += f"""
{i}. Pharmacy: {pharmacy.get('StoreName', 'N/A')}
   Address: {pharmacy.get('Address1', 'N/A')}, {pharmacy.get('City', 'N/A')}, {pharmacy.get('State', 'N/A')} {pharmacy.get('ZipCode', 'N/A')}
   Current listed states of operation: {pharmacy.get('Operates in states', 'N/A')}
   NCPDP ID: {pharmacy.get('NCPDPID', 'N/A')}
"""

        prompt += """

For each pharmacy, provide your response in this EXACT JSON format:
{
  "validations": [
    {
      "pharmacy_index": 1,
      "is_correct": true/false,
      "corrected_states": "Only provide if different from original - use same format as input",
      "confidence": "high/medium/low",
      "reasoning": "Brief explanation of your findings"
    }
  ]
}

Only include "corrected_states" if the original information is incorrect. Use the same format as the input (e.g., "Nationwide", "State1, State2, State3", or "All states except State1").
"""
        
        return prompt

    def validate_batch_with_openai(self, batch: List[Dict]) -> List[Dict]:
        """Validate a batch of pharmacies using OpenAI o3-deepresearch."""
        
        prompt = self.create_validation_prompt(batch)
        
        try:
            logger.info(f"Validating batch of {len(batch)} pharmacies...")
            
            response = self.client.chat.completions.create(
                model="o3-deepresearch",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a healthcare regulatory expert. Provide accurate, fact-based analysis of pharmacy licensing and operations."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                max_completion_tokens=4000
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            logger.debug(f"OpenAI response: {response_text}")
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                json_str = response_text[start_idx:end_idx]
                
                result = json.loads(json_str)
                validations = result.get('validations', [])
                
                logger.info(f"Successfully parsed {len(validations)} validations")
                return validations
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response_text}")
                
                # Return default results for this batch
                return [
                    {
                        "pharmacy_index": i + 1,
                        "is_correct": None,
                        "corrected_states": "",
                        "confidence": "error",
                        "reasoning": "Failed to parse OpenAI response"
                    } for i in range(len(batch))
                ]
                
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            
            # Return default results for this batch
            return [
                {
                    "pharmacy_index": i + 1,
                    "is_correct": None,
                    "corrected_states": "",
                    "confidence": "error",
                    "reasoning": f"API error: {str(e)}"
                } for i in range(len(batch))
            ]

    def process_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the entire CSV in batches."""
        
        # Add new columns
        df['Initial states of operation correct'] = None
        df['States of operation by OpenAI deepresearch'] = ""
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
            
            # Validate with OpenAI
            validations = self.validate_batch_with_openai(batch_pharmacies)
            
            # Apply results back to dataframe
            for validation in validations:
                try:
                    pharmacy_idx = validation.get('pharmacy_index', 1) - 1  # Convert to 0-based
                    actual_idx = batch_idx + pharmacy_idx
                    
                    if actual_idx < len(df):
                        df.loc[actual_idx, 'Initial states of operation correct'] = validation.get('is_correct')
                        df.loc[actual_idx, 'States of operation by OpenAI deepresearch'] = validation.get('corrected_states', '')
                        df.loc[actual_idx, 'Validation confidence'] = validation.get('confidence', '')
                        df.loc[actual_idx, 'Validation reasoning'] = validation.get('reasoning', '')
                        
                except Exception as e:
                    logger.error(f"Error applying validation result: {str(e)}")
                    continue
            
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
            
            logger.info(f"\nValidation Summary:")
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
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILENAME):
        logger.error(f"CSV file '{CSV_FILENAME}' not found!")
        logger.error("Please ensure the CSV file is in the same directory as this script.")
        sys.exit(1)
    
    # Initialize validator
    validator = PharmacyStateValidator()
    
    # Load CSV
    df = validator.load_csv(CSV_FILENAME)
    
    # Process CSV
    validated_df = validator.process_csv(df)
    
    # Save results
    validator.save_results(validated_df, OUTPUT_FILENAME)
    
    logger.info("Validation completed successfully!")
    logger.info(f"Check the output file: {OUTPUT_FILENAME}")


if __name__ == "__main__":
    main()