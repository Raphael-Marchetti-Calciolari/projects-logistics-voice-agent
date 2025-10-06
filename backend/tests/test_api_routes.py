"""
Integration tests for API routes.
Tests the router layer without external dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from constants import SCENARIO_CHECKIN, CALL_STATUS_INITIATED
from exceptions import (
    AgentConfigurationError,
    ConfigurationNotFoundError,
    CallNotFoundError
)


class TestCallRoutes:
    """Test call-related API routes."""
    
    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_call_service(self):
        """Mock call service."""
        with patch('routers.calls.call_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        with patch('routers.calls.db_service') as mock:
            yield mock
    
    def test_initiate_web_call_success(self, client, mock_call_service):
        """Test POST /api/calls/initiate-web endpoint."""
        # Setup
        mock_call_service.initiate_web_call = AsyncMock(return_value={
            "call_id": "call-123",
            "retell_call_id": "retell-789",
            "access_token": "token-xyz",
            "status": CALL_STATUS_INITIATED
        })
        
        # Execute
        response = client.post("/api/calls/initiate-web", json={
            "driver_name": "John Doe",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["call_id"] == "call-123"
        assert data["access_token"] == "token-xyz"
    
    def test_initiate_web_call_invalid_request(self, client):
        """Test web call with invalid request data."""
        # Execute - missing required fields
        response = client.post("/api/calls/initiate-web", json={
            "driver_name": "John Doe"
            # Missing load_number and scenario_type
        })
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_initiate_web_call_no_agent(self, client, mock_call_service):
        """Test web call when agent not configured."""
        # Setup
        mock_call_service.initiate_web_call = AsyncMock(
            side_effect=AgentConfigurationError(SCENARIO_CHECKIN)
        )
        
        # Execute
        response = client.post("/api/calls/initiate-web", json={
            "driver_name": "John Doe",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN
        })
        
        # Assert
        assert response.status_code == 400
    
    def test_initiate_phone_call_success(self, client, mock_call_service):
        """Test POST /api/calls/initiate endpoint."""
        # Setup
        mock_call_service.initiate_phone_call = AsyncMock(return_value={
            "call_id": "call-123",
            "retell_call_id": "retell-789",
            "status": CALL_STATUS_INITIATED
        })
        
        # Execute
        response = client.post("/api/calls/initiate", json={
            "driver_name": "John Doe",
            "driver_phone": "+14155551234",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["call_id"] == "call-123"
        assert data["retell_call_id"] == "retell-789"
    
    def test_initiate_phone_call_invalid_phone(self, client):
        """Test phone call with invalid phone number format."""
        # Execute
        response = client.post("/api/calls/initiate", json={
            "driver_name": "John Doe",
            "driver_phone": "invalid-phone",
            "load_number": "LOAD-456",
            "scenario_type": SCENARIO_CHECKIN
        })
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_list_calls_success(self, client, mock_db_service):
        """Test GET /api/calls endpoint."""
        # Setup
        mock_db_service.list_call_logs.return_value = [
            {
                "id": "call-1",
                "driver_name": "John Doe",
                "call_status": "completed",
                "scenario_type": SCENARIO_CHECKIN
            },
            {
                "id": "call-2",
                "driver_name": "Jane Smith",
                "call_status": "initiated",
                "scenario_type": SCENARIO_CHECKIN
            }
        ]
        
        # Execute
        response = client.get("/api/calls")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["driver_name"] == "John Doe"
    
    def test_list_calls_with_ordering(self, client, mock_db_service):
        """Test GET /api/calls with ordering parameters."""
        # Setup
        mock_db_service.list_call_logs.return_value = []
        
        # Execute
        response = client.get("/api/calls?order_by=created_at&ascending=true")
        
        # Assert
        assert response.status_code == 200
        mock_db_service.list_call_logs.assert_called_once_with(
            order_by="created_at",
            ascending=True
        )
    
    def test_get_call_success(self, client, mock_db_service):
        """Test GET /api/calls/{call_id} endpoint."""
        # Setup
        call_id = "call-123"
        mock_db_service.get_call_log.return_value = {
            "id": call_id,
            "driver_name": "John Doe",
            "call_status": "completed",
            "scenario_type": SCENARIO_CHECKIN,
            "raw_transcript": "Test transcript",
            "structured_data": {"location": "123 Main St"}
        }
        
        # Execute
        response = client.get(f"/api/calls/{call_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == call_id
        assert data["driver_name"] == "John Doe"
        assert data["raw_transcript"] == "Test transcript"
    
    def test_get_call_not_found(self, client, mock_db_service):
        """Test GET /api/calls/{call_id} when call doesn't exist."""
        # Setup
        mock_db_service.get_call_log.side_effect = CallNotFoundError("call-999")
        
        # Execute
        response = client.get("/api/calls/call-999")
        
        # Assert
        assert response.status_code == 404


class TestConfigurationRoutes:
    """Test configuration-related API routes."""
    
    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_config_service(self):
        """Mock configuration service."""
        with patch('routers.configurations.config_service') as mock:
            yield mock
    
    def test_create_configuration_success(self, client, mock_config_service):
        """Test POST /api/configurations endpoint."""
        # Setup
        mock_config_service.save_configuration = AsyncMock(return_value={
            "id": "config-123",
            "scenario_type": SCENARIO_CHECKIN,
            "system_prompt": "Test prompt",
            "retell_settings": {"voice_id": "11labs-Adrian"},
            "llm_id": "llm-123",
            "agent_id": "agent-123",
            "created_at": "2024-01-01T00:00:00Z"
        })
        
        # Execute
        response = client.post("/api/configurations", json={
            "scenario_type": SCENARIO_CHECKIN,
            "system_prompt": "Test prompt for checkin",
            "retell_settings": {
                "voice_id": "11labs-Adrian",
                "enable_backchannel": True,
                "voice_speed": 1.0
            }
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_type"] == SCENARIO_CHECKIN
        assert data["llm_id"] == "llm-123"
        assert data["agent_id"] == "agent-123"
    
    def test_create_configuration_invalid_scenario(self, client):
        """Test configuration with invalid scenario type."""
        # Execute
        response = client.post("/api/configurations", json={
            "scenario_type": "invalid_type",
            "system_prompt": "Test prompt",
            "retell_settings": {"voice_id": "11labs-Adrian"}
        })
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_get_configuration_success(self, client, mock_config_service):
        """Test GET /api/configurations/{scenario_type} endpoint."""
        # Setup
        mock_config_service.get_configuration.return_value = {
            "id": "config-123",
            "scenario_type": SCENARIO_CHECKIN,
            "system_prompt": "Test prompt",
            "retell_settings": {},
            "llm_id": "llm-123",
            "agent_id": "agent-123",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Execute
        response = client.get(f"/api/configurations/{SCENARIO_CHECKIN}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_type"] == SCENARIO_CHECKIN
    
    def test_get_configuration_not_found(self, client, mock_config_service):
        """Test GET configuration when it doesn't exist."""
        # Setup
        mock_config_service.get_configuration.side_effect = ConfigurationNotFoundError(SCENARIO_CHECKIN)
        
        # Execute
        response = client.get(f"/api/configurations/{SCENARIO_CHECKIN}")
        
        # Assert
        assert response.status_code == 404
    
    def test_list_configurations_success(self, client, mock_config_service):
        """Test GET /api/configurations endpoint."""
        # Setup
        mock_config_service.list_configurations.return_value = [
            {
                "id": "config-1",
                "scenario_type": SCENARIO_CHECKIN,
                "system_prompt": "Checkin prompt",
                "retell_settings": {},
                "llm_id": "llm-1",
                "agent_id": "agent-1",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        # Execute
        response = client.get("/api/configurations")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["scenario_type"] == SCENARIO_CHECKIN


class TestWebhookRoutes:
    """Test webhook-related API routes."""
    
    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_webhook_service(self):
        """Mock webhook service."""
        with patch('routers.webhooks.webhook_service') as mock:
            yield mock
    
    def test_handle_call_started_webhook(self, client, mock_webhook_service):
        """Test POST /api/webhooks/retell with call_started event."""
        # Setup
        mock_webhook_service.handle_call_started = AsyncMock()
        
        # Execute
        response = client.post("/api/webhooks/retell", json={
            "event": "call_started",
            "call": {
                "call_id": "retell-call-789"
            }
        })
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_webhook_service.handle_call_started.assert_called_once_with("retell-call-789")
    
    def test_handle_call_ended_webhook(self, client, mock_webhook_service):
        """Test POST /api/webhooks/retell with call_ended event."""
        # Setup
        mock_webhook_service.handle_call_ended = AsyncMock()
        transcript = "Sample call transcript"
        
        # Execute
        response = client.post("/api/webhooks/retell", json={
            "event": "call_ended",
            "call": {
                "call_id": "retell-call-789",
                "transcript": transcript
            }
        })
        
        # Assert
        assert response.status_code == 200
        mock_webhook_service.handle_call_ended.assert_called_once_with(
            "retell-call-789",
            transcript
        )
    
    def test_handle_call_analyzed_webhook(self, client, mock_webhook_service):
        """Test POST /api/webhooks/retell with call_analyzed event."""
        # Setup
        mock_webhook_service.handle_call_analyzed = AsyncMock()
        
        # Execute
        response = client.post("/api/webhooks/retell", json={
            "event": "call_analyzed",
            "call": {
                "call_id": "retell-call-789",
                "transcript": "Analysis transcript"
            }
        })
        
        # Assert
        assert response.status_code == 200
        mock_webhook_service.handle_call_analyzed.assert_called_once()
    
    def test_handle_unknown_webhook_event(self, client, mock_webhook_service):
        """Test webhook with unknown event type."""
        # Execute
        response = client.post("/api/webhooks/retell", json={
            "event": "unknown_event",
            "call": {
                "call_id": "retell-call-789"
            }
        })
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        # Should not call any handler
        mock_webhook_service.handle_call_started.assert_not_called()
        mock_webhook_service.handle_call_ended.assert_not_called()
        mock_webhook_service.handle_call_analyzed.assert_not_called()
