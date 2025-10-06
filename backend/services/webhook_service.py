"""
Service layer for webhook processing operations.
"""

from typing import Dict, Any
from services.database_service import db_service
from openai_client import openai_extractor
from constants import (
    CALL_STATUS_IN_PROGRESS,
    CALL_STATUS_COMPLETED,
    SCENARIO_CHECKIN,
    SCENARIO_EMERGENCY
)
from logger import service_logger
import json


class WebhookService:
    """Service class for webhook processing."""
    
    def __init__(self):
        self.db_service = db_service
        self.extractor = openai_extractor
    
    # PUBLIC_INTERFACE
    async def handle_call_started(self, call_id: str) -> None:
        """
        Handle call_started webhook event.
        
        Args:
            call_id: Retell call ID
        """
        try:
            self.db_service.update_call_log(
                call_id,
                {"call_status": CALL_STATUS_IN_PROGRESS},
                id_field="retell_call_id"
            )
            service_logger.info(f"Call started: {call_id}")
        except Exception as e:
            service_logger.error(f"Error handling call_started: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def handle_call_ended(self, call_id: str, transcript: str = None) -> None:
        """
        Handle call_ended webhook event.
        
        Args:
            call_id: Retell call ID
            transcript: Call transcript if available
        """
        try:
            if transcript:
                service_logger.info(f"Call ended with transcript: {call_id}")
                await self.process_transcript(call_id, transcript)
            else:
                service_logger.info(f"Call ended without transcript: {call_id}")
                self.db_service.update_call_log(
                    call_id,
                    {"call_status": CALL_STATUS_COMPLETED},
                    id_field="retell_call_id"
                )
        except Exception as e:
            service_logger.error(f"Error handling call_ended: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def handle_call_analyzed(self, call_id: str, transcript: str = None) -> None:
        """
        Handle call_analyzed webhook event.
        
        Args:
            call_id: Retell call ID
            transcript: Call transcript if available
        """
        try:
            if transcript:
                service_logger.info(f"Call analyzed with transcript: {call_id}")
                await self.process_transcript(call_id, transcript)
            else:
                service_logger.warning(f"Call analyzed without transcript: {call_id}")
        except Exception as e:
            service_logger.error(f"Error handling call_analyzed: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def process_transcript(self, call_id: str, transcript: str) -> None:
        """
        Process and store transcript with structured data extraction.
        
        Args:
            call_id: Retell call ID
            transcript: Call transcript text
        """
        try:
            # Get call info
            call_info = self.db_service.get_call_by_retell_id(call_id)
            
            if not call_info:
                service_logger.error(f"Call {call_id} not found in database")
                return
            
            scenario_type = call_info["scenario_type"]
            service_logger.info(f"Extracting structured data for {scenario_type} scenario")
            
            # Extract structured data based on scenario
            structured_data = await self._extract_data(scenario_type, transcript)
            
            if structured_data:
                service_logger.debug(f"Extracted data: {json.dumps(structured_data, indent=2)}")
            
            # Update database
            self.db_service.update_call_log(
                call_id,
                {
                    "raw_transcript": transcript,
                    "structured_data": structured_data,
                    "call_status": CALL_STATUS_COMPLETED
                },
                id_field="retell_call_id"
            )
            
            service_logger.info(f"Stored transcript and structured data for call {call_id}")
        except Exception as e:
            service_logger.error(f"Error processing transcript: {e}")
            # Still save the transcript even if extraction fails
            try:
                self.db_service.update_call_log(
                    call_id,
                    {
                        "raw_transcript": transcript,
                        "call_status": CALL_STATUS_COMPLETED
                    },
                    id_field="retell_call_id"
                )
                service_logger.info("Stored transcript only (extraction failed)")
            except Exception as save_error:
                service_logger.error(f"Failed to save transcript: {save_error}")
    
    async def _extract_data(self, scenario_type: str, transcript: str) -> Dict[str, Any]:
        """
        Extract structured data based on scenario type.
        
        Args:
            scenario_type: Type of scenario
            transcript: Call transcript
            
        Returns:
            Extracted structured data dictionary
        """
        if scenario_type == SCENARIO_CHECKIN:
            return await self.extractor.extract_checkin_data(transcript)
        elif scenario_type == SCENARIO_EMERGENCY:
            return await self.extractor.extract_emergency_data(transcript)
        else:
            service_logger.warning(f"Unknown scenario type: {scenario_type}")
            return None


# Singleton instance
webhook_service = WebhookService()
