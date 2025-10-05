import os
from retell import AsyncRetell
from typing import Dict, Any

class RetellClient:
    def __init__(self):
        self.api_key = os.getenv("RETELL_API_KEY")
        if not self.api_key:
            raise ValueError("RETELL_API_KEY must be set")
        
        self.client = AsyncRetell(api_key=self.api_key)
    
    async def create_llm(self, general_prompt: str) -> str:
        """Create LLM and return ID"""
        llm = await self.client.llm.create(
            general_prompt=general_prompt,
            model="gpt-4o"
        )
        return llm.llm_id
    
    async def create_agent(self, agent_name: str, llm_id: str) -> Dict[str, Any]:
        """Create agent - exactly like the working test"""
        agent = await self.client.agent.create(
            agent_name=agent_name,
            voice_id="11labs-Adrian",
            response_engine={
                "type": "retell-llm",
                "llm_id": llm_id
            }
        )
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name
        }

# Singleton
retell_client = RetellClient()
