import asyncio
import os
from dotenv import load_dotenv
from retell import AsyncRetell
from database import supabase

load_dotenv()

async def verify_agents():
    """Check if database agent_ids exist in Retell"""
    
    client = AsyncRetell(api_key=os.getenv("RETELL_API_KEY"))
    
    # Get agents from database
    result = supabase.table("agent_configurations").select("*").execute()
    
    print("=" * 60)
    print("VERIFYING AGENTS IN RETELL")
    print("=" * 60)
    
    # Get all agents from Retell
    print("\n1️⃣ Fetching agents from Retell...")
    retell_agents = await client.agent.list()
    print(f"   Found {len(retell_agents)} agents in Retell")
    
    retell_agent_ids = {agent.agent_id for agent in retell_agents}
    
    print("\n2️⃣ Checking database agents...")
    for config in result.data:
        scenario = config['scenario_type']
        agent_id = config.get('agent_id')
        
        if agent_id:
            exists = agent_id in retell_agent_ids
            status = "✅ EXISTS" if exists else "❌ NOT FOUND"
            print(f"   {scenario}: {agent_id} - {status}")
        else:
            print(f"   {scenario}: No agent_id - ⚠️ MISSING")
    
    print("\n3️⃣ All Retell agents:")
    for agent in retell_agents:
        print(f"   - {agent.agent_name}: {agent.agent_id}")

if __name__ == "__main__":
    asyncio.run(verify_agents())
