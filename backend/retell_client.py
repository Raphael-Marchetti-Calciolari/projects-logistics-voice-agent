"""
Retell AI client for managing LLMs, agents, and calls.
"""

import os
from retell import AsyncRetell
from typing import Dict, Any, Optional, List
from constants import RETELL_VOICE_ID, RETELL_MODEL
from logger import service_logger


class RetellClient:
    """Client for interacting with Retell AI API."""
    
    def __init__(self):
        """Initialize Retell client."""
        self.api_key = os.getenv("RETELL_API_KEY")
        if not self.api_key:
            raise ValueError("RETELL_API_KEY must be set")
        
        self.client = AsyncRetell(api_key=self.api_key)
    
    # PUBLIC_INTERFACE
    async def create_llm(
        self,
        general_prompt: str,
        general_tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Create LLM with optional tools and return ID.
        
        Args:
            general_prompt: System prompt for the LLM
            general_tools: Optional list of tools for the LLM
            
        Returns:
            LLM ID
        """
        llm_config = {
            "general_prompt": general_prompt,
            "model": RETELL_MODEL
        }
        
        # Add tools if provided
        if general_tools:
            llm_config["general_tools"] = general_tools
        
        try:
            llm = await self.client.llm.create(**llm_config)
            service_logger.debug(f"Created LLM: {llm.llm_id}")
            return llm.llm_id
        except Exception as e:
            service_logger.error(f"Error creating LLM: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def update_llm(
        self,
        llm_id: str,
        general_prompt: Optional[str] = None,
        general_tools: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Update an existing LLM.
        
        Args:
            llm_id: ID of the LLM to update
            general_prompt: Optional new system prompt
            general_tools: Optional new list of tools
        """
        update_data = {}
        
        if general_prompt is not None:
            update_data["general_prompt"] = general_prompt
        
        if general_tools is not None:
            update_data["general_tools"] = general_tools
        
        if update_data:
            try:
                await self.client.llm.update(llm_id, **update_data)
                service_logger.debug(f"Updated LLM: {llm_id}")
            except Exception as e:
                service_logger.error(f"Error updating LLM: {e}")
                raise
    
    # PUBLIC_INTERFACE
    async def create_agent(self, agent_name: str, llm_id: str) -> Dict[str, Any]:
        """
        Create agent linked to an LLM.
        
        Args:
            agent_name: Name for the agent
            llm_id: ID of the LLM to use
            
        Returns:
            Dictionary with agent_id and agent_name
        """
        try:
            agent = await self.client.agent.create(
                agent_name=agent_name,
                voice_id=RETELL_VOICE_ID,
                response_engine={
                    "type": "retell-llm",
                    "llm_id": llm_id
                },
                enable_backchannel=True
            )
            service_logger.debug(f"Created agent: {agent.agent_id}")
            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name
            }
        except Exception as e:
            service_logger.error(f"Error creating agent: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def create_web_call(
        self,
        agent_id: str,
        dynamic_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a web call (browser-based, no phone number needed).
        
        Args:
            agent_id: ID of the agent to use
            dynamic_variables: Optional variables to pass to the agent
            
        Returns:
            Dictionary with call_id and access_token
        """
        try:
            call = await self.client.call.create_web_call(
                agent_id=agent_id,
                retell_llm_dynamic_variables=dynamic_variables or {}
            )
            service_logger.debug(f"Created web call: {call.call_id}")
            return {
                "call_id": call.call_id,
                "access_token": call.access_token
            }
        except Exception as e:
            service_logger.error(f"Error creating web call: {e}")
            raise
    
    # PUBLIC_INTERFACE
    async def create_phone_call(
        self,
        agent_id: str,
        from_number: str,
        to_number: str,
        dynamic_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Initiate a phone call.
        
        Args:
            agent_id: ID of the agent to use
            from_number: Phone number to call from
            to_number: Phone number to call to
            dynamic_variables: Optional variables to pass to the agent
            
        Returns:
            Dictionary with call_id
        """
        try:
            call = await self.client.call.create_phone_call(
                from_number=from_number,
                to_number=to_number,
                override_agent_id=agent_id,
                retell_llm_dynamic_variables=dynamic_variables or {}
            )
            service_logger.debug(f"Created phone call: {call.call_id}")
            return {
                "call_id": call.call_id
            }
        except Exception as e:
            service_logger.error(f"Error creating phone call: {e}")
            raise


# Singleton instance
retell_client = RetellClient()
