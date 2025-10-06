"""
Tests for call service - handles call initiation logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from constants import SCENARIO_CHECKIN, CALL_STATUS_INITIATED, WEB_CALL_PHONE_MARKER
from exceptions import (
    AgentConfigurationError,
    CallLogCreationError,
    EnvironmentVariableError,
    InvalidPhoneNumberError
)


class TestCallService:
    """Test call initiation operations."""
    
    @pytest.fixture
    def call_service(self):
        """Get call service with mocked dependencies."""
        from services.call_service import CallService
        return CallService()
    
    async def test_initiate_web_call_success(self, call_service):
        """Test successful web call initiation."""
        # Setup mocks
        sample_call_record = {
            "id": "call-uuid-123",
            "driver_name": "John Doe",
            "driver_phone": WEB_CALL_PHONE_MARKER,
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN,
            "call_status": CALL_STATUS_INITIATED,
            "retell_call_id": None
        }
        
        call_service.db_service = MagicMock()
        call_service.db_service.get_agent_id.return_value = "agent-123"
        call_service.db_service.create_call_log.return_value = sample_call_record
        call_service.db_service.update_call_log.return_value = None
        
        call_service.retell_client = MagicMock()
        call_service.retell_client.create_web_call = AsyncMock(return_value={
            "call_id": "retell-call-789",
            "access_token": "token-xyz"
        })
        
        # Execute
        result = await call_service.initiate_web_call(
            driver_name="John Doe",
            load_number="LOAD-456",
            scenario_type=SCENARIO_CHECKIN
        )
        
        # Assert
        assert result["call_id"] == "call-uuid-123"
        assert result["retell_call_id"] == "retell-call-789"
        assert result["access_token"] == "token-xyz"
        assert result["status"] == CALL_STATUS_INITIATED
        
        # Verify web call marker was used
        create_call_args = call_service.db_service.create_call_log.call_args[0][0]
        assert create_call_args["driver_phone"] == WEB_CALL_PHONE_MARKER
    
    async def test_initiate_web_call_no_agent(self, call_service):
        """Test web call fails when agent not configured."""
        # Setup
        call_service.db_service = MagicMock()
        call_service.db_service.get_agent_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(AgentConfigurationError):
            await call_service.initiate_web_call(
                driver_name="John Doe",
                load_number="LOAD-456",
                scenario_type=SCENARIO_CHECKIN
            )
    
    @patch.dict('os.environ', {'RETELL_FROM_NUMBER': '+14155559999'})
    async def test_initiate_phone_call_success(self, call_service):
        """Test successful phone call initiation."""
        # Setup
        sample_call_record = {
            "id": "call-uuid-123",
            "driver_name": "John Doe",
            "driver_phone": "+14155551234",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN,
            "call_status": CALL_STATUS_INITIATED,
            "retell_call_id": None
        }
        
        call_service.db_service = MagicMock()
        call_service.db_service.get_agent_id.return_value = "agent-123"
        call_service.db_service.create_call_log.return_value = sample_call_record
        call_service.db_service.update_call_log.return_value = None
        
        call_service.retell_client = MagicMock()
        call_service.retell_client.create_phone_call = AsyncMock(return_value={
            "call_id": "retell-call-789"
        })
        
        # Execute
        result = await call_service.initiate_phone_call(
            driver_name="John Doe",
            driver_phone="+14155551234",
            load_number="LOAD-456",
            scenario_type=SCENARIO_CHECKIN
        )
        
        # Assert
        assert result["call_id"] == "call-uuid-123"
        assert result["retell_call_id"] == "retell-call-789"
        assert result["status"] == CALL_STATUS_INITIATED
        call_service.retell_client.create_phone_call.assert_called_once()
    
    @patch.dict('os.environ', {}, clear=True)
    async def test_initiate_phone_call_no_from_number(self, call_service):
        """Test phone call fails when RETELL_FROM_NUMBER not set."""
        # Setup
        call_service.db_service = MagicMock()
        call_service.db_service.get_agent_id.return_value = "agent-123"
        
        # Execute & Assert
        with pytest.raises(EnvironmentVariableError):
            await call_service.initiate_phone_call(
                driver_name="John Doe",
                driver_phone="+14155551234",
                load_number="LOAD-456",
                scenario_type=SCENARIO_CHECKIN
            )
    
    @patch.dict('os.environ', {'RETELL_FROM_NUMBER': '+14155551234'})
    async def test_initiate_phone_call_same_number(self, call_service):
        """Test phone call fails when calling same number as from_number."""
        # Setup
        call_service.db_service = MagicMock()
        call_service.db_service.get_agent_id.return_value = "agent-123"
        
        # Execute & Assert
        with pytest.raises(InvalidPhoneNumberError):
            await call_service.initiate_phone_call(
                driver_name="John Doe",
                driver_phone="+14155551234",  # Same as FROM_NUMBER
                load_number="LOAD-456",
                scenario_type=SCENARIO_CHECKIN
            )
    
    @patch.dict('os.environ', {'RETELL_FROM_NUMBER': '+14155559999'})
    @patch.dict('os.environ', {'RETELL_FROM_NUMBER': '+14155559999'})
    async def test_initiate_phone_call_no_agent(self, call_service):
        """Test phone call fails when agent not configured."""
        # Setup
        call_service.db_service = MagicMock()
        call_service.db_service.get_agent_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(AgentConfigurationError):
            await call_service.initiate_phone_call(
                driver_name="John Doe",
                driver_phone="+14155551234",
                load_number="LOAD-456",
                scenario_type=SCENARIO_CHECKIN
            )
    
    def test_create_call_log_success(self, call_service):
        """Test call log creation."""
        # Setup
        sample_call_record = {
            "id": "call-uuid-123",
            "driver_name": "John Doe",
            "driver_phone": "+14155551234",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN,
            "call_status": CALL_STATUS_INITIATED
        }
        
        call_service.db_service = MagicMock()
        call_service.db_service.create_call_log.return_value = sample_call_record
        
        # Execute
        result = call_service._create_call_log(
            driver_name="John Doe",
            driver_phone="+14155551234",
            load_number="LOAD-456",
            scenario_type=SCENARIO_CHECKIN
        )
        
        # Assert
        assert result == sample_call_record
        call_service.db_service.create_call_log.assert_called_once()
    
    def test_create_call_log_failure(self, call_service):
        """Test call log creation failure."""
        # Setup
        call_service.db_service = MagicMock()
        call_service.db_service.create_call_log.side_effect = Exception("Database error")
        
        # Execute & Assert
        with pytest.raises(CallLogCreationError):
            call_service._create_call_log(
                driver_name="John Doe",
                driver_phone="+14155551234",
                load_number="LOAD-456",
                scenario_type=SCENARIO_CHECKIN
            )
