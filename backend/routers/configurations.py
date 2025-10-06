from fastapi import APIRouter, HTTPException
from models import ConfigurationCreate, ConfigurationResponse
from database import supabase
from retell_client import retell_client

router = APIRouter(prefix="/api/configurations", tags=["configurations"])

# Define the end_call tool
END_CALL_TOOL = {
    "type": "end_call",
    "name": "end_call",
    "description": "End the call when: 1) All required information has been collected and goodbye has been said, 2) After 3 attempts to get information from an uncooperative driver who only gives single-word responses, 3) Emergency information has been gathered and escalation statement has been made. Always say a brief farewell before ending."
}

async def sync_retell_agent(config_id: str, scenario_type: str, system_prompt: str):
    """Create or update Retell LLM and agent, store IDs in database"""
    
    try:
        # Get existing config to check for IDs
        result = supabase.table("agent_configurations")\
            .select("llm_id, agent_id")\
            .eq("id", config_id)\
            .execute()
        
        existing = result.data[0] if result.data else {}
        llm_id = existing.get("llm_id")
        agent_id = existing.get("agent_id")
        
        # Create LLM if it doesn't exist
        if not llm_id:
            print(f"Creating new {scenario_type} LLM with end_call tool...")
            llm_id = await retell_client.create_llm(
                general_prompt=system_prompt,
                general_tools=[END_CALL_TOOL]
            )
            print(f"✅ Created {scenario_type} LLM: {llm_id}")
            
            # Store LLM ID in database
            supabase.table("agent_configurations")\
                .update({"llm_id": llm_id})\
                .eq("id", config_id)\
                .execute()
        else:
            # Update existing LLM with new prompt and ensure end_call tool is present
            print(f"Updating existing {scenario_type} LLM with end_call tool...")
            await retell_client.update_llm(
                llm_id=llm_id,
                general_prompt=system_prompt,
                general_tools=[END_CALL_TOOL]
            )
            print(f"✅ Updated {scenario_type} LLM")
        
        # Create agent if it doesn't exist
        if not agent_id:
            print(f"Creating new {scenario_type} agent...")
            agent_name = f"Dispatch {scenario_type.title()} Agent"
            agent_result = await retell_client.create_agent(agent_name, llm_id)
            agent_id = agent_result['agent_id']
            print(f"✅ Created {scenario_type} agent: {agent_id}")
            
            # Store agent ID in database
            supabase.table("agent_configurations")\
                .update({"agent_id": agent_id})\
                .eq("id", config_id)\
                .execute()
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing Retell: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@router.post("", response_model=ConfigurationResponse)
async def create_configuration(config: ConfigurationCreate):
    """Create or update agent configuration"""
    try:
        existing = supabase.table("agent_configurations")\
            .select("*")\
            .eq("scenario_type", config.scenario_type)\
            .execute()
        
        data = {
            "scenario_type": config.scenario_type,
            "system_prompt": config.system_prompt,
            "retell_settings": config.retell_settings.model_dump()
        }
        
        if existing.data:
            result = supabase.table("agent_configurations")\
                .update(data)\
                .eq("scenario_type", config.scenario_type)\
                .execute()
        else:
            result = supabase.table("agent_configurations")\
                .insert(data)\
                .execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
        
        # Sync with Retell and store IDs
        config_record = result.data[0]
        await sync_retell_agent(
            config_record['id'],
            config.scenario_type,
            config.system_prompt
        )
        
        # Fetch updated record with IDs
        updated = supabase.table("agent_configurations")\
            .select("*")\
            .eq("id", config_record['id'])\
            .execute()
        
        return updated.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scenario_type}", response_model=ConfigurationResponse)
def get_configuration(scenario_type: str):
    """Get configuration for a specific scenario"""
    if scenario_type not in ["checkin", "emergency"]:
        raise HTTPException(status_code=400, detail="Invalid scenario type")
    
    try:
        result = supabase.table("agent_configurations")\
            .select("*")\
            .eq("scenario_type", scenario_type)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Configuration for {scenario_type} not found")
        
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=list[ConfigurationResponse])
def list_configurations():
    """Get all configurations"""
    try:
        result = supabase.table("agent_configurations")\
            .select("*")\
            .order("scenario_type")\
            .execute()
        
        return result.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
