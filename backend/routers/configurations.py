"""
FastAPI router for agent configuration endpoints.
"""

from fastapi import APIRouter, HTTPException
from models import ConfigurationCreate, ConfigurationResponse
from services.configuration_service import config_service
from exceptions import ConfigurationNotFoundError
from logger import router_logger

router = APIRouter(prefix="/api/configurations", tags=["configurations"])


# PUBLIC_INTERFACE
@router.post("", response_model=ConfigurationResponse)
async def create_configuration(config: ConfigurationCreate):
    """
    Create or update agent configuration.
    
    Args:
        config: Configuration data
        
    Returns:
        Created/updated configuration with agent IDs
        
    Raises:
        HTTPException: If configuration save fails
    """
    try:
        result = await config_service.save_configuration(
            scenario_type=config.scenario_type,
            system_prompt=config.system_prompt,
            retell_settings=config.retell_settings.model_dump()
        )
        return result
    except Exception as e:
        router_logger.error(f"Error saving configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# PUBLIC_INTERFACE
@router.get("/{scenario_type}", response_model=ConfigurationResponse)
def get_configuration(scenario_type: str):
    """
    Get configuration for a specific scenario.
    
    Args:
        scenario_type: Type of scenario (checkin, emergency)
        
    Returns:
        Configuration data
        
    Raises:
        HTTPException: If configuration not found or invalid
    """
    try:
        return config_service.get_configuration(scenario_type)
    except ValueError as e:
        router_logger.warning(f"Invalid scenario type: {scenario_type}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConfigurationNotFoundError as e:
        router_logger.warning(f"Configuration not found: {scenario_type}")
        raise
    except Exception as e:
        router_logger.error(f"Error fetching configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# PUBLIC_INTERFACE
@router.get("", response_model=list[ConfigurationResponse])
def list_configurations():
    """
    Get all configurations.
    
    Returns:
        List of all agent configurations
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        return config_service.list_configurations()
    except Exception as e:
        router_logger.error(f"Error listing configurations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
