"""
Tests for configuration service - manages agent configurations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from constants import SCENARIO_CHECKIN, SCENARIO_EMERGENCY
from exceptions import ConfigurationNotFoundError


class TestConfigurationService:
    """Test configuration management operations."""
    
    @pytest.fixture
    def config_service(self):
        """Get config service with mocked dependencies."""
        from services.configuration_service import ConfigurationService
        return ConfigurationService()
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "id": "test-config-id",
            "scenario_type": SCENARIO_CHECKIN,
            "system_prompt": "Test prompt for checkin scenario",
            "retell_settings": {
                "voice_id": "11labs-Adrian",
                "enable_backchannel": True
            },
            "llm_id": "test-llm-id",
            "agent_id": "test-agent-id",
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    async def test_save_configuration_new(self, config_service, sample_config):
        """Test creating a new configuration."""
        # Setup
        config_service.db_service = MagicMock()
        config_service.db_service.save_configuration.return_value = sample_config.copy()
        config_service.db_service.get_agent_configuration.side_effect = [
            {**sample_config, "llm_id": None, "agent_id": None},  # First call (before sync)
            sample_config  # Second call (after sync)
        ]
        
        config_service.retell_client = MagicMock()
        config_service.retell_client.create_llm = AsyncMock(return_value="new-llm-id")
        config_service.retell_client.create_agent = AsyncMock(return_value={"agent_id": "new-agent-id"})
        
        # Execute
        result = await config_service.save_configuration(
            scenario_type=SCENARIO_CHECKIN,
            system_prompt="Test prompt",
            retell_settings={"voice_id": "11labs-Adrian"}
        )
        
        # Assert
        assert result["scenario_type"] == SCENARIO_CHECKIN
        config_service.db_service.save_configuration.assert_called()
        config_service.retell_client.create_llm.assert_called_once()
        config_service.retell_client.create_agent.assert_called_once()
    
    async def test_save_configuration_update_existing(self, config_service, sample_config):
        """Test updating an existing configuration."""
        # Setup
        config_service.db_service = MagicMock()
        config_service.db_service.save_configuration.return_value = sample_config
        config_service.db_service.get_agent_configuration.return_value = sample_config
        
        config_service.retell_client = MagicMock()
        config_service.retell_client.update_llm = AsyncMock()
        
        # Execute
        result = await config_service.save_configuration(
            scenario_type=SCENARIO_CHECKIN,
            system_prompt="Updated prompt",
            retell_settings={"voice_id": "11labs-Adrian"}
        )
        
        # Assert
        assert result["scenario_type"] == SCENARIO_CHECKIN
        config_service.retell_client.update_llm.assert_called_once()
    
    def test_get_configuration_success(self, config_service, sample_config):
        """Test retrieving a configuration."""
        # Setup
        config_service.db_service = MagicMock()
        config_service.db_service.get_agent_configuration.return_value = sample_config
        
        # Execute
        result = config_service.get_configuration(SCENARIO_CHECKIN)
        
        # Assert
        assert result == sample_config
        config_service.db_service.get_agent_configuration.assert_called_once_with(SCENARIO_CHECKIN)
    
    def test_get_configuration_not_found(self, config_service):
        """Test retrieving a non-existent configuration."""
        # Setup
        config_service.db_service = MagicMock()
        config_service.db_service.get_agent_configuration.return_value = None
        
        # Execute & Assert
        with pytest.raises(ConfigurationNotFoundError):
            config_service.get_configuration(SCENARIO_CHECKIN)
    
    def test_get_configuration_invalid_scenario(self, config_service):
        """Test with invalid scenario type."""
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid scenario type"):
            config_service.get_configuration("invalid_scenario")
    
    def test_list_configurations(self, config_service, sample_config):
        """Test listing all configurations."""
        # Setup
        emergency_config = {**sample_config, "scenario_type": SCENARIO_EMERGENCY}
        
        config_service.db_service = MagicMock()
        config_service.db_service.list_configurations.return_value = [sample_config, emergency_config]
        
        # Execute
        result = config_service.list_configurations()
        
        # Assert
        assert len(result) == 2
        assert result[0]["scenario_type"] == SCENARIO_CHECKIN
        assert result[1]["scenario_type"] == SCENARIO_EMERGENCY
        config_service.db_service.list_configurations.assert_called_once()
    
    async def test_sync_retell_agent_creates_llm_and_agent(self, config_service):
        """Test Retell sync creates both LLM and agent when missing."""
        # Setup
        config_without_ids = {
            "llm_id": None,
            "agent_id": None
        }
        
        config_service.db_service = MagicMock()
        config_service.db_service.get_agent_configuration.return_value = config_without_ids
        config_service.db_service.save_configuration.return_value = None
        
        config_service.retell_client = MagicMock()
        config_service.retell_client.create_llm = AsyncMock(return_value="new-llm-id")
        config_service.retell_client.create_agent = AsyncMock(return_value={"agent_id": "new-agent-id"})
        
        # Execute
        result = await config_service._sync_retell_agent(
            config_id="test-id",
            scenario_type=SCENARIO_CHECKIN,
            system_prompt="Test prompt"
        )
        
        # Assert
        assert result is True
        config_service.retell_client.create_llm.assert_called_once()
        config_service.retell_client.create_agent.assert_called_once()
        assert config_service.db_service.save_configuration.call_count == 2  # Once for LLM, once for agent
