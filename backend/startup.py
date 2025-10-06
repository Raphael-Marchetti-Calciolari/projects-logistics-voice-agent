import asyncio
from database import supabase
from retell_client import retell_client
from default_prompts import CHECKIN_PROMPT, EMERGENCY_PROMPT, DEFAULT_RETELL_SETTINGS

async def ensure_agent_exists(scenario_type: str, system_prompt: str):
    """Check if agent exists, create if not"""
    
    try:
        # Check if configuration exists
        result = supabase.table("agent_configurations")\
            .select("*")\
            .eq("scenario_type", scenario_type)\
            .execute()
        
        if result.data:
            config = result.data[0]
            
            # Check if agent_id exists
            if config.get("agent_id"):
                print(f"✅ {scenario_type.title()} agent already exists: {config['agent_id']}")
                return config["agent_id"]
            else:
                print(f"⚠️  {scenario_type.title()} config exists but no agent_id, creating...")
                config_id = config["id"]
        else:
            print(f"📝 Creating {scenario_type} configuration...")
            # Create configuration
            insert_result = supabase.table("agent_configurations")\
                .insert({
                    "scenario_type": scenario_type,
                    "system_prompt": system_prompt,
                    "retell_settings": DEFAULT_RETELL_SETTINGS
                })\
                .execute()
            
            config_id = insert_result.data[0]["id"]
            print(f"✅ Created {scenario_type} configuration")
        
        # Create LLM
        print(f"🤖 Creating {scenario_type} LLM...")
        llm_id = await retell_client.create_llm(system_prompt)
        print(f"✅ Created LLM: {llm_id}")
        
        # Update config with LLM ID
        supabase.table("agent_configurations")\
            .update({"llm_id": llm_id})\
            .eq("id", config_id)\
            .execute()
        
        # Create agent
        print(f"📞 Creating {scenario_type} agent...")
        agent_name = f"Dispatch {scenario_type.title()} Agent"
        agent_result = await retell_client.create_agent(agent_name, llm_id)
        agent_id = agent_result['agent_id']
        print(f"✅ Created agent: {agent_id}")
        
        # Update config with agent ID
        supabase.table("agent_configurations")\
            .update({"agent_id": agent_id})\
            .eq("id", config_id)\
            .execute()
        
        print(f"✅ {scenario_type.title()} agent fully configured\n")
        return agent_id
        
    except Exception as e:
        print(f"❌ Error ensuring {scenario_type} agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def initialize_agents():
    """Initialize both check-in and emergency agents on startup"""
    print("\n" + "="*60)
    print("INITIALIZING LOGISTICS VOICE AGENTS")
    print("="*60 + "\n")
    
    # Ensure check-in agent exists
    await ensure_agent_exists("checkin", CHECKIN_PROMPT)
    
    # Ensure emergency agent exists
    await ensure_agent_exists("emergency", EMERGENCY_PROMPT)
    
    print("="*60)
    print("AGENT INITIALIZATION COMPLETE")
    print("="*60 + "\n")

def run_startup():
    """Synchronous wrapper for startup"""
    asyncio.run(initialize_agents())
