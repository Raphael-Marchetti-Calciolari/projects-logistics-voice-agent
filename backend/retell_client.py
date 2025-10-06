import os
from retell import AsyncRetell
from typing import Dict, Any, Optional, List

class RetellClient:
    def __init__(self):
        self.api_key = os.getenv("RETELL_API_KEY")
        if not self.api_key:
            raise ValueError("RETELL_API_KEY must be set")
        
        self.client = AsyncRetell(api_key=self.api_key)
    
    async def create_llm(
        self, 
        general_prompt: str,
        general_tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Create LLM with optional tools and return ID"""
        llm_config = {
            "general_prompt": general_prompt,
            "model": "gpt-4o"
        }
        
        # Add tools if provided
        if general_tools:
            llm_config["general_tools"] = general_tools
        
        llm = await self.client.llm.create(**llm_config)
        return llm.llm_id
    
    async def update_llm(
        self,
        llm_id: str,
        general_prompt: Optional[str] = None,
        general_tools: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Update an existing LLM"""
        update_data = {}
        
        if general_prompt is not None:
            update_data["general_prompt"] = general_prompt
        
        if general_tools is not None:
            update_data["general_tools"] = general_tools
        
        if update_data:
            await self.client.llm.update(llm_id, **update_data)
    
    async def create_agent(self, agent_name: str, llm_id: str) -> Dict[str, Any]:
        """Create agent"""
        agent = await self.client.agent.create(
            agent_name=agent_name,
            voice_id="11labs-Adrian",
            response_engine={
                "type": "retell-llm",
                "llm_id": llm_id
            },
            enable_backchannel=True
        )
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name
        }
    
    async def create_web_call(
        self,
        agent_id: str,
        dynamic_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a web call (browser-based, no phone number needed)"""
        call = await self.client.call.create_web_call(
            agent_id=agent_id,
            retell_llm_dynamic_variables=dynamic_variables or {}
        )
        return {
            "call_id": call.call_id,
            "access_token": call.access_token
        }
    
    async def create_phone_call(
        self,
        agent_id: str,
        from_number: str,
        to_number: str,
        dynamic_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Initiate a phone call"""
        call = await self.client.call.create_phone_call(
            from_number=from_number,
            to_number=to_number,
            override_agent_id=agent_id,
            retell_llm_dynamic_variables=dynamic_variables or {}
        )
        return {
            "call_id": call.call_id
        }

# Singleton
retell_client = RetellClient()
