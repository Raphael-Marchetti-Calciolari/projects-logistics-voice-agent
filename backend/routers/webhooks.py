"""
FastAPI router for webhook endpoints.
"""

from fastapi import APIRouter, Request, HTTPException
from services.webhook_service import webhook_service
from logger import router_logger
import json

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


# PUBLIC_INTERFACE
@router.post("/retell")
async def handle_retell_webhook(request: Request):
    """
    Handle webhooks from Retell AI.
    
    Processes different webhook events:
    - call_started: Mark call as in progress
    - call_ended: Process transcript if available
    - call_analyzed: Process transcript data
    
    Args:
        request: FastAPI request object with webhook payload
        
    Returns:
        Status response
        
    Raises:
        HTTPException: If webhook processing fails
    """
    try:
        body = await request.body()
        data = json.loads(body)
        
        event = data.get("event")
        call_data = data.get("call", {})
        call_id = call_data.get("call_id")
        
        router_logger.info(f"Webhook received: {event} | Call: {call_id}")
        
        # Route to appropriate handler
        if event == "call_started":
            await webhook_service.handle_call_started(call_id)
        elif event == "call_ended":
            transcript = call_data.get("transcript", "")
            await webhook_service.handle_call_ended(call_id, transcript)
        elif event == "call_analyzed":
            transcript = call_data.get("transcript", "")
            await webhook_service.handle_call_analyzed(call_id, transcript)
        else:
            router_logger.warning(f"Unknown webhook event: {event}")
        
        return {"status": "ok"}
    except Exception as e:
        router_logger.error(f"Webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
