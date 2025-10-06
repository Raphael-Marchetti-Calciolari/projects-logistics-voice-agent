"""
FastAPI router for call-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from services.call_service import call_service
from services.database_service import db_service
from models import WebCallInitiateRequest, WebCallInitiateResponse
from logger import router_logger
from exceptions import (
    AgentConfigurationError,
    CallLogCreationError,
    EnvironmentVariableError,
    InvalidPhoneNumberError,
    CallNotFoundError
)

router = APIRouter(prefix="/api/calls", tags=["calls"])


class CallInitiateRequest(BaseModel):
    """Request model for initiating a phone call."""
    driver_name: str = Field(..., min_length=1, description="Driver's name")
    driver_phone: str = Field(
        ..., 
        pattern=r'^\+?1?\d{10,15}$',
        description="Driver's phone number in E.164 format"
    )
    load_number: str = Field(..., min_length=1, description="Load number")
    scenario_type: str = Field(
        ..., 
        pattern="^(checkin|emergency)$",
        description="Type of scenario: checkin or emergency"
    )


class CallInitiateResponse(BaseModel):
    """Response model for phone call initiation."""
    call_id: str
    retell_call_id: str
    status: str


# PUBLIC_INTERFACE
@router.post("/initiate-web", response_model=WebCallInitiateResponse)
async def initiate_web_call(request: WebCallInitiateRequest):
    """
    Initiate a web call (browser-based, no phone needed).
    
    Args:
        request: Web call initiation request
        
    Returns:
        Web call response with access token
        
    Raises:
        HTTPException: If call initiation fails
    """
    try:
        result = await call_service.initiate_web_call(
            driver_name=request.driver_name,
            load_number=request.load_number,
            scenario_type=request.scenario_type
        )
        return result
    except (AgentConfigurationError, CallLogCreationError) as e:
        router_logger.error(f"Web call initiation failed: {e.detail}")
        raise
    except Exception as e:
        router_logger.error(f"Unexpected error in web call initiation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# PUBLIC_INTERFACE
@router.post("/initiate", response_model=CallInitiateResponse)
async def initiate_call(request: CallInitiateRequest):
    """
    Initiate a phone call to a driver.
    
    Args:
        request: Call initiation request
        
    Returns:
        Call response with call IDs
        
    Raises:
        HTTPException: If call initiation fails
    """
    try:
        result = await call_service.initiate_phone_call(
            driver_name=request.driver_name,
            driver_phone=request.driver_phone,
            load_number=request.load_number,
            scenario_type=request.scenario_type
        )
        return result
    except (
        EnvironmentVariableError,
        InvalidPhoneNumberError,
        AgentConfigurationError,
        CallLogCreationError
    ) as e:
        router_logger.error(f"Phone call initiation failed: {e.detail}")
        raise
    except Exception as e:
        router_logger.error(f"Unexpected error in phone call initiation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# PUBLIC_INTERFACE
@router.get("", summary="List all calls")
async def list_calls(
    order_by: str = Query(default="created_at", description="Field to order by"),
    ascending: bool = Query(default=False, description="Sort order (true=ascending, false=descending)")
):
    """
    List all call logs with optional ordering.
    
    Args:
        order_by: Field to order by (default: created_at)
        ascending: Sort order direction (default: False for descending)
        
    Returns:
        List of call logs
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        calls = db_service.list_call_logs(order_by=order_by, ascending=ascending)
        return calls
    except Exception as e:
        router_logger.error(f"Error listing calls: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# PUBLIC_INTERFACE
@router.get("/{call_id}")
async def get_call(call_id: str):
    """
    Get call details by ID.
    
    Args:
        call_id: UUID of the call
        
    Returns:
        Call log details
        
    Raises:
        HTTPException: If call not found or error occurs
    """
    try:
        return db_service.get_call_log(call_id)
    except CallNotFoundError as e:
        router_logger.warning(f"Call not found: {call_id}")
        raise
    except Exception as e:
        router_logger.error(f"Error fetching call {call_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
