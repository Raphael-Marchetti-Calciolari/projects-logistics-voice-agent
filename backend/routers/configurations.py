from fastapi import APIRouter, HTTPException
from models import ConfigurationCreate, ConfigurationResponse, ConfigurationUpdate
from database import supabase
from datetime import datetime

router = APIRouter(prefix="/api/configurations", tags=["configurations"])

@router.post("", response_model=ConfigurationResponse)
def create_configuration(config: ConfigurationCreate):
    """Create or update agent configuration for a scenario"""
    try:
        # Check if configuration already exists for this scenario
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
            # Update existing configuration
            result = supabase.table("agent_configurations")\
                .update(data)\
                .eq("scenario_type", config.scenario_type)\
                .execute()
        else:
            # Insert new configuration
            result = supabase.table("agent_configurations")\
                .insert(data)\
                .execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
        
        return result.data[0]
    
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
