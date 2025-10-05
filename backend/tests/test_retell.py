import os
from dotenv import load_dotenv
from retell import AsyncRetell
import asyncio

load_dotenv()

async def test_retell():
    api_key = os.getenv("RETELL_API_KEY")
    print(f"Testing with API key: {api_key[:15]}...")
    
    try:
        client = AsyncRetell(api_key=api_key)
        
        # Try to list existing agents
        print("\n1. Testing: List agents...")
        agents = await client.agent.list()
        print(f"SUCCESS: Found {len(agents)} agents")
        for agent in agents:
            print(f"  - {agent.agent_name} (ID: {agent.agent_id})")
        
        # Try to create an LLM
        print("\n2. Testing: Create LLM...")
        llm = await client.llm.create(
            general_prompt="Test prompt for logistics voice agent",
            model="gpt-4o"
        )
        print(f"SUCCESS: Created LLM with ID: {llm.llm_id}")
        
        # Try to create an agent
        print("\n3. Testing: Create agent...")
        agent = await client.agent.create(
            agent_name="Test Logistics Agent",
            voice_id="11labs-Adrian",
            response_engine={
                "type": "retell-llm",
                "llm_id": llm.llm_id
            }
        )
        print(f"SUCCESS: Created agent with ID: {agent.agent_id}")
        
        print("\n✅ ALL TESTS PASSED!")
        print(f"\nCheck your Retell dashboard now:")
        print(f"https://beta.retellai.com/dashboard")
        print(f"You should see 'Test Logistics Agent'")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_retell())
