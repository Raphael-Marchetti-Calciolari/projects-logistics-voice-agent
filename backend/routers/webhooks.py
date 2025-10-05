from fastapi import APIRouter, Request, HTTPException
from database import supabase
import os

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("/retell")
async def handle_retell_webhook(request: Request):
    """Handle webhooks from Retell AI"""
    try:
        # Get raw body
        body = await request.body()
        
        # Parse webhook data
        import json
        data = json.loads(body)
        
        event = data.get("event")
        call_data = data.get("call", {})
        call_id = call_data.get("call_id")
        
        print(f"📞 Webhook received: {event} for call {call_id}")
        
        # Handle different webhook events
        if event == "call_started":
            supabase.table("call_logs")\
                .update({"call_status": "in_progress"})\
                .eq("retell_call_id", call_id)\
                .execute()
            print(f"✅ Updated call {call_id} to in_progress")
        
        elif event == "call_ended":
            supabase.table("call_logs")\
                .update({"call_status": "completed"})\
                .eq("retell_call_id", call_id)\
                .execute()
            print(f"✅ Call {call_id} ended")
        
        elif event == "call_analyzed":
            transcript = call_data.get("transcript", "")
            
            supabase.table("call_logs")\
                .update({
                    "raw_transcript": transcript,
                    "call_status": "completed"
                })\
                .eq("retell_call_id", call_id)\
                .execute()
            
            print(f"✅ Stored transcript for call {call_id}")
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
