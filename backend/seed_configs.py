import asyncio
import httpx

async def seed_configurations():
    """Create initial agent configurations"""
    
    checkin_config = {
        "scenario_type": "checkin",
        "system_prompt": """You are a professional dispatch agent calling a truck driver about their load.

Your goal is to get a status update on the load. Be friendly but efficient.

Dynamic variables you'll receive:
- driver_name: The driver's name
- load_number: The load identifier

Opening: "Hi {driver_name}, this is Dispatch calling about load {load_number}. Can you give me a quick update on your status?"

Based on their response:
- If driving: Ask about current location, ETA, any delays
- If arrived: Ask about unloading status, door number
- Before ending: Remind them about POD (Proof of Delivery) documentation

Keep the conversation natural and conversational. Listen to what they say and adapt your questions accordingly.""",
        "retell_settings": {
            "enable_backchannel": True,
            "backchannel_frequency": 0.8,
            "interruption_sensitivity": 0.7,
            "ambient_sound": "off",
            "ambient_sound_volume": 0.3,
            "voice_temperature": 1.0,
            "voice_speed": 1.0,
            "responsiveness": 1.0,
            "voice_id": "11labs-Adrian"
        }
    }
    
    print("Creating check-in configuration...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/configurations",
            json=checkin_config,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Check-in config created")
            print(f"   LLM ID: {data.get('llm_id', 'pending...')}")
            print(f"   Agent ID: {data.get('agent_id', 'pending...')}")
            
            # Wait a bit for Retell sync
            print("\n⏳ Waiting for Retell sync...")
            await asyncio.sleep(3)
            
            # Verify
            response = await client.get("http://localhost:8000/api/configurations/checkin")
            data = response.json()
            print(f"\n✅ Verified:")
            print(f"   LLM ID: {data.get('llm_id')}")
            print(f"   Agent ID: {data.get('agent_id')}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    print("=" * 60)
    print("SEEDING AGENT CONFIGURATIONS")
    print("=" * 60)
    print("\nMake sure backend is running on http://localhost:8000\n")
    
    asyncio.run(seed_configurations())
