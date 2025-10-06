"""
Tests for webhook service - processes Retell webhook events.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from constants import (
    CALL_STATUS_IN_PROGRESS,
    CALL_STATUS_COMPLETED,
    SCENARIO_CHECKIN,
    SCENARIO_EMERGENCY
)


class TestWebhookService:
    """Test webhook processing operations."""
    
    @pytest.fixture
    def webhook_service(self):
        """Get webhook service with mocked dependencies."""
        from services.webhook_service import WebhookService
        return WebhookService()
    
    @pytest.fixture
    def sample_call_info(self):
        """Sample call information."""
        return {
            "id": "call-uuid-123",
            "retell_call_id": "retell-call-789",
            "driver_name": "John Doe",
            "driver_phone": "+14155551234",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN,
            "call_status": CALL_STATUS_IN_PROGRESS
        }
    
    @pytest.fixture
    def sample_transcript(self):
        """Sample call transcript."""
        return """
        Agent: Hi John, this is dispatch calling for your check-in. How are you doing today?
        Driver: Hey, I'm doing good, just made it to the delivery location.
        Agent: Great! Can you confirm your current location?
        Driver: Yeah, I'm at 123 Main Street in Springfield.
        Agent: Perfect. Any issues with the delivery or the truck?
        Driver: No issues at all, everything went smoothly.
        Agent: Excellent! What's your estimated time of departure?
        Driver: I should be leaving in about 30 minutes.
        Agent: Got it. Thanks for checking in John, drive safe!
        Driver: Thanks, will do!
        """
    
    async def test_handle_call_started(self, webhook_service):
        """Test call_started event updates status to in_progress."""
        # Setup
        call_id = "retell-call-789"
        webhook_service.db_service = MagicMock()
        
        # Execute
        await webhook_service.handle_call_started(call_id)
        
        # Assert
        webhook_service.db_service.update_call_log.assert_called_once_with(
            call_id,
            {"call_status": CALL_STATUS_IN_PROGRESS},
            id_field="retell_call_id"
        )
    
    async def test_handle_call_ended_with_transcript(self, webhook_service, sample_call_info, sample_transcript):
        """Test call_ended event with transcript processes it."""
        # Setup
        call_id = "retell-call-789"
        webhook_service.db_service = MagicMock()
        webhook_service.db_service.get_call_by_retell_id.return_value = sample_call_info
        webhook_service.process_transcript = AsyncMock()
        
        # Execute
        await webhook_service.handle_call_ended(call_id, sample_transcript)
        
        # Assert
        webhook_service.process_transcript.assert_called_once_with(call_id, sample_transcript)
    
    async def test_handle_call_ended_without_transcript(self, webhook_service):
        """Test call_ended event without transcript just updates status."""
        # Setup
        call_id = "retell-call-789"
        webhook_service.db_service = MagicMock()
        
        # Execute
        await webhook_service.handle_call_ended(call_id)
        
        # Assert
        webhook_service.db_service.update_call_log.assert_called_once_with(
            call_id,
            {"call_status": CALL_STATUS_COMPLETED},
            id_field="retell_call_id"
        )
    
    async def test_handle_call_analyzed_with_transcript(self, webhook_service, sample_call_info, sample_transcript):
        """Test call_analyzed event with transcript processes it."""
        # Setup
        call_id = "retell-call-789"
        webhook_service.db_service = MagicMock()
        webhook_service.db_service.get_call_by_retell_id.return_value = sample_call_info
        webhook_service.process_transcript = AsyncMock()
        
        # Execute
        await webhook_service.handle_call_analyzed(call_id, sample_transcript)
        
        # Assert
        webhook_service.process_transcript.assert_called_once_with(call_id, sample_transcript)
    
    async def test_process_transcript_checkin_scenario(
        self,
        webhook_service,
        sample_call_info,
        sample_transcript
    ):
        """Test transcript processing for checkin scenario."""
        # Setup
        webhook_service.db_service = MagicMock()
        webhook_service.db_service.get_call_by_retell_id.return_value = sample_call_info
        
        extracted_data = {
            "current_location": "123 Main Street, Springfield",
            "delivery_status": "completed",
            "any_issues": False,
            "eta_departure": "30 minutes"
        }
        
        webhook_service.extractor = MagicMock()
        webhook_service.extractor.extract_checkin_data = AsyncMock(return_value=extracted_data)
        
        # Execute
        await webhook_service.process_transcript("retell-call-789", sample_transcript)
        
        # Assert
        webhook_service.extractor.extract_checkin_data.assert_called_once_with(sample_transcript)
        webhook_service.db_service.update_call_log.assert_called_once()
        
        # Verify update includes transcript and structured data
        update_args = webhook_service.db_service.update_call_log.call_args[0]
        assert update_args[1]["raw_transcript"] == sample_transcript
        assert update_args[1]["structured_data"] == extracted_data
        assert update_args[1]["call_status"] == CALL_STATUS_COMPLETED
    
    async def test_process_transcript_emergency_scenario(
        self,
        webhook_service,
        sample_call_info
    ):
        """Test transcript processing for emergency scenario."""
        # Setup
        emergency_call = {**sample_call_info, "scenario_type": SCENARIO_EMERGENCY}
        emergency_transcript = "Driver reports engine overheating on Highway 101 near mile marker 50"
        
        webhook_service.db_service = MagicMock()
        webhook_service.db_service.get_call_by_retell_id.return_value = emergency_call
        
        extracted_data = {
            "emergency_type": "mechanical",
            "issue_description": "engine overheating",
            "location": "Highway 101 near mile marker 50",
            "driver_safe": True
        }
        
        webhook_service.extractor = MagicMock()
        webhook_service.extractor.extract_emergency_data = AsyncMock(return_value=extracted_data)
        
        # Execute
        await webhook_service.process_transcript("retell-call-789", emergency_transcript)
        
        # Assert
        webhook_service.extractor.extract_emergency_data.assert_called_once_with(emergency_transcript)
        webhook_service.db_service.update_call_log.assert_called_once()
    
    async def test_process_transcript_call_not_found(self, webhook_service, sample_transcript):
        """Test transcript processing when call not found in database."""
        # Setup
        webhook_service.db_service = MagicMock()
        webhook_service.db_service.get_call_by_retell_id.return_value = None
        
        # Execute (should not raise exception, just log)
        await webhook_service.process_transcript("unknown-call", sample_transcript)
        
        # Assert - no update should be made
        webhook_service.db_service.update_call_log.assert_not_called()
    
    async def test_process_transcript_extraction_fails(
        self,
        webhook_service,
        sample_call_info,
        sample_transcript
    ):
        """Test transcript still saved when extraction fails."""
        # Setup
        webhook_service.db_service = MagicMock()
        webhook_service.db_service.get_call_by_retell_id.return_value = sample_call_info
        
        webhook_service.extractor = MagicMock()
        webhook_service.extractor.extract_checkin_data = AsyncMock(side_effect=Exception("OpenAI API error"))
        
        # Execute
        await webhook_service.process_transcript("retell-call-789", sample_transcript)
        
        # Assert - transcript should still be saved
        assert webhook_service.db_service.update_call_log.call_count == 1
        
        # Call should save transcript only (in the fallback path)
        fallback_update = webhook_service.db_service.update_call_log.call_args[0]
        assert fallback_update[1]["raw_transcript"] == sample_transcript
        assert fallback_update[1]["call_status"] == CALL_STATUS_COMPLETED
    
    async def test_extract_data_unknown_scenario(self, webhook_service):
        """Test data extraction with unknown scenario type."""
        # Execute
        result = await webhook_service._extract_data("unknown_scenario", "some transcript")
        
        # Assert
        assert result is None
