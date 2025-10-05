from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from database import supabase
from retell_client import retell_client
from models import WebCallInitiateRequest, WebCallInitiateResponse
from datetime import datetime
import os

router = APIRouter(prefix="/api/calls", tags=["calls"])

class CallInitiateRequest(BaseModel):
    driver_name: str = Field(..., min_length=1)
    driver_phone: str = Field(..., pattern=r'^\+?1?\d{10,15}$')
    load_number: str = Field(..., min_length=1)
    scenario_type: str = Field(..., pattern="^(checkin|emergency)$")

class CallInitiateResponse(BaseModel):
    call_id: str
    retell_call_id: str
    status: str

@router.post("/initiate-web", response_model=WebCallInitiateResponse)
async def initiate_web_call(request: WebCallInitiateRequest):
    """Initiate a web call (browser-based, no phone needed)"""
    try:
        # Get agent configuration for this scenario
        config = supabase.table("agent_configurations")\
            .select("agent_id")\
            .eq("scenario_type", request.scenario_type)\
            .execute()
        
        if not config.data or not config.data[0].get("agent_id"):
            raise HTTPException(
                status_code=400,
                detail=f"No agent configured for {request.scenario_type} scenario"
            )
        
        agent_id = config.data[0]["agent_id"]
        
        # Create call log record
        call_log = supabase.table("call_logs").insert({
            "driver_name": request.driver_name,
            "driver_phone": "web-call",  # Special marker for web calls
            "load_number": request.load_number,
            "scenario_type": request.scenario_type,
            "call_status": "initiated"
        }).execute()
        
        if not call_log.data:
            raise HTTPException(status_code=500, detail="Failed to create call log")
        
        call_record = call_log.data[0]
        
        # Create web call via Retell
        retell_call = await retell_client.create_web_call(
            agent_id=agent_id,
            dynamic_variables={
                "driver_name": request.driver_name,
                "load_number": request.load_number
            }
        )
        
        # Update call log with Retell call ID
        supabase.table("call_logs")\
            .update({"retell_call_id": retell_call["call_id"]})\
            .eq("id", call_record["id"])\
            .execute()
        
        print(f"✅ Initiated web call for {request.driver_name}: {retell_call['call_id']}")
        
        return {
            "call_id": call_record["id"],
            "retell_call_id": retell_call["call_id"],
            "access_token": retell_call["access_token"],
            "status": "initiated"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error initiating web call: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initiate", response_model=CallInitiateResponse)
async def initiate_call(request: CallInitiateRequest):
    """Initiate a phone call to a driver"""
    try:
        # Get from_number from environment
        from_number = os.getenv("RETELL_FROM_NUMBER")
        if not from_number:
            raise HTTPException(
                status_code=500,
                detail="RETELL_FROM_NUMBER not configured"
            )
        
        # Validate from_number != to_number
        if from_number == request.driver_phone:
            raise HTTPException(
                status_code=400,
                detail="Cannot call the same number as the from_number. Use a different driver phone number."
            )
        
        # Get agent configuration for this scenario
        config = supabase.table("agent_configurations")\
            .select("agent_id")\
            .eq("scenario_type", request.scenario_type)\
            .execute()
        
        if not config.data or not config.data[0].get("agent_id"):
            raise HTTPException(
                status_code=400,
                detail=f"No agent configured for {request.scenario_type} scenario"
            )
        
        agent_id = config.data[0]["agent_id"]
        
        # Create call log record
        call_log = supabase.table("call_logs").insert({
            "driver_name": request.driver_name,
            "driver_phone": request.driver_phone,
            "load_number": request.load_number,
            "scenario_type": request.scenario_type,
            "call_status": "initiated"
        }).execute()
        
        if not call_log.data:
            raise HTTPException(status_code=500, detail="Failed to create call log")
        
        call_record = call_log.data[0]
        
        # Initiate call via Retell
        retell_call = await retell_client.create_phone_call(
            agent_id=agent_id,
            from_number=from_number,
            to_number=request.driver_phone,
            dynamic_variables={
                "driver_name": request.driver_name,
                "load_number": request.load_number
            }
        )
        
        # Update call log with Retell call ID
        supabase.table("call_logs")\
            .update({"retell_call_id": retell_call["call_id"]})\
            .eq("id", call_record["id"])\
            .execute()
        
        print(f"✅ Initiated call to {request.driver_name}: {retell_call['call_id']}")
        
        return {
            "call_id": call_record["id"],
            "retell_call_id": retell_call["call_id"],
            "status": "initiated"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error initiating call: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{call_id}")
async def get_call(call_id: str):
    """Get call details by ID"""
    try:
        result = supabase.table("call_logs")\
            .select("*")\
            .eq("id", call_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
