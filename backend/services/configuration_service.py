"""
Service layer for agent configuration operations.
"""

from typing import Dict, Any, List
from services.database_service import db_service
from retell_client import retell_client
from constants import END_CALL_TOOL, VALID_SCENARIOS
from exceptions import ConfigurationNotFoundError
from logger import service_logger


class ConfigurationService:
    """Service class for configuration operations."""
    
    def __init__(self):
        self.db_service = db_service
        self.retell_client = retell_client
    
    # PUBLIC_INTERFACE
    async def save_configuration(
        self,
        scenario_type: str,
        system_prompt: str,
        retell_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create or update agent configuration and sync with Retell.
        
        Args:
            scenario_type: Scenario type (checkin, emergency)
            system_prompt: System prompt for the agent
            retell_settings: Retell voice settings
            
        Returns:
            Updated configuration with agent IDs
        """
        # Save configuration to database
        config_data = {
            "scenario_type": scenario_type,
            "system_prompt": system_prompt,
            "retell_settings": retell_settings
        }
        
        config_record = self.db_service.save_configuration(scenario_type, config_data)
        
        # Sync with Retell
        await self._sync_retell_agent(
            config_record['id'],
            scenario_type,
            system_prompt
        )
        
        # Return updated configuration
        return self.db_service.get_agent_configuration(scenario_type)
    
    # PUBLIC_INTERFACE
    def get_configuration(self, scenario_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific scenario.
        
        Args:
            scenario_type: Scenario type
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationNotFoundError: If configuration not found
        """
        if scenario_type not in VALID_SCENARIOS:
            raise ValueError(f"Invalid scenario type: {scenario_type}")
        
        config = self.db_service.get_agent_configuration(scenario_type)
        if not config:
            raise ConfigurationNotFoundError(scenario_type)
        
        return config
    
    # PUBLIC_INTERFACE
    def list_configurations(self) -> List[Dict[str, Any]]:
        """
        Get all configurations.
        
        Returns:
            List of configuration dictionaries
        """
        return self.db_service.list_configurations()
    
    async def _sync_retell_agent(
        self,
        config_id: str,
        scenario_type: str,
        system_prompt: str
    ) -> bool:
        """
        Create or update Retell LLM and agent, store IDs in database.
        
        Args:
            config_id: Configuration record ID
            scenario_type: Scenario type
            system_prompt: System prompt
            
        Returns:
            True if successful
        """
        try:
            config = self.db_service.get_agent_configuration(scenario_type)
            llm_id = config.get("llm_id") if config else None
            agent_id = config.get("agent_id") if config else None
            
            # Create or update LLM
            if not llm_id:
                service_logger.info(f"Creating new {scenario_type} LLM with end_call tool")
                llm_id = await self.retell_client.create_llm(
                    general_prompt=system_prompt,
                    general_tools=[END_CALL_TOOL]
                )
                service_logger.info(f"Created {scenario_type} LLM: {llm_id}")
                
                # Update database with LLM ID
                self.db_service.save_configuration(
                    scenario_type,
                    {"llm_id": llm_id}
                )
            else:
                service_logger.info(f"Updating existing {scenario_type} LLM")
                await self.retell_client.update_llm(
                    llm_id=llm_id,
                    general_prompt=system_prompt,
                    general_tools=[END_CALL_TOOL]
                )
                service_logger.info(f"Updated {scenario_type} LLM")
            
            # Create agent if it doesn't exist
            if not agent_id:
                service_logger.info(f"Creating new {scenario_type} agent")
                agent_name = f"Dispatch {scenario_type.title()} Agent"
                agent_result = await self.retell_client.create_agent(agent_name, llm_id)
                agent_id = agent_result['agent_id']
                service_logger.info(f"Created {scenario_type} agent: {agent_id}")
                
                # Update database with agent ID
                self.db_service.save_configuration(
                    scenario_type,
                    {"agent_id": agent_id}
                )
            
            return True
        except Exception as e:
            service_logger.error(f"Error syncing Retell: {e}", exc_info=True)
            return False


# Singleton instance
config_service = ConfigurationService()
