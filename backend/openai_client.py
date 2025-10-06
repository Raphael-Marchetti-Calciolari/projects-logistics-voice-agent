"""
OpenAI client for transcript data extraction.
"""

import os
from openai import AsyncOpenAI
from typing import Dict, Any
from constants import OPENAI_MODEL, OPENAI_TEMPERATURE
from logger import service_logger
import json


class OpenAIExtractor:
    """Client for extracting structured data from call transcripts using OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    # PUBLIC_INTERFACE
    async def extract_checkin_data(self, transcript: str) -> Dict[str, Any]:
        """
        Extract structured data from check-in call transcript.
        
        Args:
            transcript: Raw call transcript text
            
        Returns:
            Dictionary with extracted check-in data fields
        """
        prompt = self._build_checkin_prompt(transcript)
        
        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction assistant. Return only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            service_logger.debug(f"Successfully extracted check-in data")
            return result
        except Exception as e:
            service_logger.error(f"Error extracting check-in data: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def extract_emergency_data(self, transcript: str) -> Dict[str, Any]:
        """
        Extract structured data from emergency call transcript.
        
        Args:
            transcript: Raw call transcript text
            
        Returns:
            Dictionary with extracted emergency data fields
        """
        prompt = self._build_emergency_prompt(transcript)
        
        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction assistant. Return only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            service_logger.debug(f"Successfully extracted emergency data")
            return result
        except Exception as e:
            service_logger.error(f"Error extracting emergency data: {e}")
            raise
    
    def _build_checkin_prompt(self, transcript: str) -> str:
        """
        Build prompt for check-in data extraction.
        
        Args:
            transcript: Call transcript
            
        Returns:
            Formatted prompt string
        """
        return f"""Analyze this driver check-in call transcript and extract the following information.
Return ONLY valid JSON with these exact fields:

{{
  "call_outcome": "In-Transit Update" OR "Arrival Confirmation",
  "driver_status": "Driving" OR "Delayed" OR "Arrived" OR "Unloading",
  "current_location": "string (e.g., 'I-10 near Indio, CA')",
  "eta": "string (e.g., 'Tomorrow, 8:00 AM') or 'N/A'",
  "delay_reason": "string (e.g., 'Heavy Traffic', 'Weather', 'None')",
  "unloading_status": "string (e.g., 'In Door 42', 'Waiting for Lumper', 'N/A')",
  "pod_reminder_acknowledged": true or false
}}

Rules:
- If information is not mentioned, use "N/A" for strings and false for booleans
- Choose the most appropriate value from the options given
- Extract exactly what the driver said

Transcript:
{transcript}
"""
    
    def _build_emergency_prompt(self, transcript: str) -> str:
        """
        Build prompt for emergency data extraction.
        
        Args:
            transcript: Call transcript
            
        Returns:
            Formatted prompt string
        """
        return f"""Analyze this emergency call transcript and extract the following information.
Return ONLY valid JSON with these exact fields:

{{
  "call_outcome": "Emergency Escalation",
  "emergency_type": "Accident" OR "Breakdown" OR "Medical" OR "Other",
  "safety_status": "string (e.g., 'Driver confirmed everyone is safe')",
  "injury_status": "string (e.g., 'No injuries reported')",
  "emergency_location": "string (e.g., 'I-15 North, Mile Marker 123')",
  "load_secure": true or false,
  "escalation_status": "Connected to Human Dispatcher"
}}

Rules:
- If information is not mentioned, use "Unknown" for strings and false for booleans
- Choose the most appropriate emergency_type from the options
- Extract safety and injury information exactly as stated

Transcript:
{transcript}
"""


# Singleton instance
openai_extractor = OpenAIExtractor()
