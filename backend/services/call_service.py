"""
Service layer for call-related business logic.
"""

from typing import Dict, Any
from services.database_service import db_service
from retell_client import retell_client
from constants import (
    CALL_STATUS_INITIATED,
    WEB_CALL_PHONE_MARKER,
    VALID_SCENARIOS
)
from exceptions import (
    AgentConfigurationError,
    CallLogCreationError,
    EnvironmentVariableError,
    InvalidPhoneNumberError
)
from logger import service_logger
import os


class CallService:
    """Service class for call-related operations."""
    
    def __init__(self):
        self.db_service = db_service
        self.retell_client = retell_client
    
    # PUBLIC_INTERFACE
    async def initiate_web_call(
        self,
        driver_name: str,
        load_number: str,
        scenario_type: str
    ) -> Dict[str, Any]:
        """
        Initiate a browser-based web call.
        
        Args:
            driver_name: Driver's name
            load_number: Load number
            scenario_type: Type of scenario (checkin, emergency)
            
        Returns:
            Dictionary with call_id, retell_call_id, access_token, and status
            
        Raises:
            AgentConfigurationError: If agent not configured
            CallLogCreationError: If call log creation fails
        """
        # Validate and get agent ID
        agent_id = self._get_agent_id(scenario_type)
        
        # Create call log
        call_record = self._create_call_log(
            driver_name=driver_name,
            driver_phone=WEB_CALL_PHONE_MARKER,
            load_number=load_number,
            scenario_type=scenario_type
        )
        
        try:
            # Create web call via Retell
            retell_call = await self.retell_client.create_web_call(
                agent_id=agent_id,
                dynamic_variables={
                    "driver_name": driver_name,
                    "load_number": load_number
                }
            )
            
            # Update call log with Retell call ID
            self.db_service.update_call_log(
                call_record["id"],
                {"retell_call_id": retell_call["call_id"]}
            )
            
            service_logger.info(
                f"Initiated web call for {driver_name}: {retell_call['call_id']}"
            )
            
            return {
                "call_id": call_record["id"],
                "retell_call_id": retell_call["call_id"],
                "access_token": retell_call["access_token"],
                "status": CALL_STATUS_INITIATED
            }
        except Exception as e:
            service_logger.error(f"Error initiating web call: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def initiate_phone_call(
        self,
        driver_name: str,
        driver_phone: str,
        load_number: str,
        scenario_type: str
    ) -> Dict[str, Any]:
        """
        Initiate a phone call.
        
        Args:
            driver_name: Driver's name
            driver_phone: Driver's phone number
            load_number: Load number
            scenario_type: Type of scenario (checkin, emergency)
            
        Returns:
            Dictionary with call_id, retell_call_id, and status
            
        Raises:
            EnvironmentVariableError: If RETELL_FROM_NUMBER not set
            InvalidPhoneNumberError: If phone numbers are invalid
            AgentConfigurationError: If agent not configured
        """
        # Get and validate from_number
        from_number = os.getenv("RETELL_FROM_NUMBER")
        if not from_number:
            raise EnvironmentVariableError("RETELL_FROM_NUMBER")
        
        # Validate phone numbers
        if from_number == driver_phone:
            raise InvalidPhoneNumberError(
                "Cannot call the same number as the from_number. "
                "Use a different driver phone number."
            )
        
        # Validate and get agent ID
        agent_id = self._get_agent_id(scenario_type)
        
        # Create call log
        call_record = self._create_call_log(
            driver_name=driver_name,
            driver_phone=driver_phone,
            load_number=load_number,
            scenario_type=scenario_type
        )
        
        try:
            # Initiate call via Retell
            retell_call = await self.retell_client.create_phone_call(
                agent_id=agent_id,
                from_number=from_number,
                to_number=driver_phone,
                dynamic_variables={
                    "driver_name": driver_name,
                    "load_number": load_number
                }
            )
            
            # Update call log with Retell call ID
            self.db_service.update_call_log(
                call_record["id"],
                {"retell_call_id": retell_call["call_id"]}
            )
            
            service_logger.info(
                f"Initiated phone call to {driver_name}: {retell_call['call_id']}"
            )
            
            return {
                "call_id": call_record["id"],
                "retell_call_id": retell_call["call_id"],
                "status": CALL_STATUS_INITIATED
            }
        except Exception as e:
            service_logger.error(f"Error initiating phone call: {e}")
            raise
    
    def _get_agent_id(self, scenario_type: str) -> str:
        """
        Get agent ID for scenario type.
        
        Args:
            scenario_type: Scenario type
            
        Returns:
            Agent ID
            
        Raises:
            AgentConfigurationError: If agent not found
        """
        agent_id = self.db_service.get_agent_id(scenario_type)
        if not agent_id:
            raise AgentConfigurationError(scenario_type)
        return agent_id
    
    def _create_call_log(
        self,
        driver_name: str,
        driver_phone: str,
        load_number: str,
        scenario_type: str
    ) -> Dict[str, Any]:
        """
        Create call log entry.
        
        Args:
            driver_name: Driver's name
            driver_phone: Driver's phone number
            load_number: Load number
            scenario_type: Scenario type
            
        Returns:
            Created call record
            
        Raises:
            CallLogCreationError: If creation fails
        """
        try:
            return self.db_service.create_call_log({
                "driver_name": driver_name,
                "driver_phone": driver_phone,
                "load_number": load_number,
                "scenario_type": scenario_type,
                "call_status": CALL_STATUS_INITIATED
            })
        except Exception:
            raise CallLogCreationError()


# Singleton instance
call_service = CallService()
