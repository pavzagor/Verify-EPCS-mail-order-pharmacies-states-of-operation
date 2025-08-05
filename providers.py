#!/usr/bin/env python3
"""
AI Provider implementations for pharmacy validation.

This module provides a unified interface for different AI providers,
allowing seamless switching between OpenAI and Google Gemini.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self):
        """Initialize the provider."""
        load_dotenv()
        self.setup_client()
    
    @abstractmethod
    def setup_client(self):
        """Set up the AI client with API key."""
        pass
    
    @abstractmethod
    def validate_batch_with_ai(self, batch: List[Dict]) -> List[Dict]:
        """Validate a batch of pharmacies using the AI provider."""
        pass
    
    def create_validation_prompt(self, pharmacies_batch: List[Dict]) -> str:
        """Create a prompt for AI to validate pharmacy states of operation."""
        
        prompt = """You are a healthcare regulatory expert specializing in pharmacy licensing and operations across U.S. states. 

Your task is to verify if the listed "states of operation" for each mail-order pharmacy are accurate based on current regulatory information, licensing requirements, and known operational status.

CRITICAL: Use web search to find current, authoritative information about each pharmacy's licensing and operational status.

For each pharmacy, search and analyze:
1. **Current licensing databases**: Search state pharmacy board websites and licensing databases
2. **Regulatory compliance**: Check for current mail-order pharmacy licenses in claimed states  
3. **Company websites**: Verify operational scope on official pharmacy websites
4. **Recent regulatory changes**: Look for any recent licensing updates or restrictions
5. **Cross-reference sources**: Compare multiple authoritative sources for accuracy

IMPORTANT: Base your analysis on factual, up-to-date regulatory information found through web search, not assumptions or outdated knowledge.

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

    def parse_response(self, response_text: str, batch_size: int) -> List[Dict]:
        """Parse AI response and extract validation results."""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
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
                    "reasoning": "Failed to parse AI response"
                } for i in range(batch_size)
            ]


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    def setup_client(self):
        """Set up OpenAI client with API key."""
        try:
            import openai
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            raise
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found!")
            logger.error("Please set it using one of these methods:")
            logger.error("1. Environment variable: export OPENAI_API_KEY='your-key-here'")
            logger.error("2. Create .env file with: OPENAI_API_KEY=your-key-here")
            raise ValueError("OpenAI API key not found")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'o3-deep-research')
        logger.info("OpenAI client initialized successfully")

    def validate_batch_with_ai(self, batch: List[Dict]) -> List[Dict]:
        """Validate a batch of pharmacies using OpenAI."""
        
        prompt = self.create_validation_prompt(batch)
        
        try:
            logger.info(f"Validating batch of {len(batch)} pharmacies with OpenAI {self.model}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
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
            
            response_text = response.choices[0].message.content
            logger.debug(f"OpenAI response: {response_text}")
            
            return self.parse_response(response_text, len(batch))
                
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


class GoogleProvider(AIProvider):
    """Google Gemini provider implementation with search and URL grounding."""
    
    def setup_client(self):
        """Set up Google Gemini client with API key."""
        try:
            from google import genai
        except ImportError:
            logger.error("Google GenAI package not installed. Run: pip install google-genai")
            raise
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY not found!")
            logger.error("Please set it using one of these methods:")
            logger.error("1. Environment variable: export GOOGLE_API_KEY='your-key-here'")
            logger.error("2. Create .env file with: GOOGLE_API_KEY=your-key-here")
            raise ValueError("Google API key not found")
        
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv('GOOGLE_MODEL', 'gemini-2.5-pro')
        self.enable_search = os.getenv('ENABLE_SEARCH_GROUNDING', 'true').lower() == 'true'
        self.enable_url_grounding = os.getenv('ENABLE_URL_GROUNDING', 'true').lower() == 'true'
        
        logger.info(f"Google Gemini client initialized successfully")
        logger.info(f"Model: {self.model}")
        logger.info(f"Search grounding: {self.enable_search}")
        logger.info(f"URL grounding: {self.enable_url_grounding}")

    def create_google_validation_prompt(self, pharmacies_batch: List[Dict]) -> str:
        """Create a Google-optimized prompt with search and URL grounding hints."""
        
        # Start with base prompt
        prompt = self.create_validation_prompt(pharmacies_batch)
        
        # Add Google-specific enhancements
        if self.enable_search or self.enable_url_grounding:
            search_enhancement = """

SEARCH STRATEGY (Use Google Search to find current information):
"""
            
            if self.enable_search:
                search_enhancement += """
- Search for "[pharmacy name] licensing states" to find current operational scope
- Search for "[pharmacy name] pharmacy board license" for official records
- Search for "mail order pharmacy licensing [state name]" for state-specific requirements
"""
            
            if self.enable_url_grounding:
                search_enhancement += """
- Reference specific state pharmacy board websites:
  * "[state].gov pharmacy board" or "[state] board of pharmacy"
  * NABP (National Association of Boards of Pharmacy) database
  * State-specific pharmacy licensing verification portals
"""
                
                # Add specific URLs for major states
                search_enhancement += """
- Key regulatory websites to check:
  * https://www.nabp.pharmacy/ (National database)
  * State pharmacy board websites for license verification
  * FDA registered mail-order pharmacy databases
"""
        
            prompt += search_enhancement
        
        return prompt

    def validate_batch_with_ai(self, batch: List[Dict]) -> List[Dict]:
        """Validate a batch of pharmacies using Google Gemini with search grounding."""
        
        prompt = self.create_google_validation_prompt(batch)
        
        try:
            logger.info(f"Validating batch of {len(batch)} pharmacies with Google {self.model}...")
            
            # Prepare tools for search and URL grounding
            tools = []
            
            if self.enable_search:
                tools.append("google_search")
            
            # Create the request using the correct API structure
            generation_config = {
                "temperature": 0.1,
                "max_output_tokens": 4000
            }
            
            # Add tools if enabled  
            tools_config = None
            if tools:
                tools_config = [{"google_search": {}}] if "google_search" in tools else None
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                generation_config=generation_config,
                tools=tools_config
            )
            
            response_text = response.text
            logger.debug(f"Google Gemini response: {response_text}")
            
            return self.parse_response(response_text, len(batch))
                
        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}")
            
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


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """Factory function to get the appropriate AI provider."""
    
    if provider_name is None:
        provider_name = os.getenv('AI_PROVIDER', 'openai').lower()
    
    if provider_name == 'openai':
        return OpenAIProvider()
    elif provider_name == 'google':
        return GoogleProvider()
    else:
        logger.error(f"Unknown AI provider: {provider_name}")
        logger.error("Supported providers: 'openai', 'google'")
        raise ValueError(f"Unknown AI provider: {provider_name}")