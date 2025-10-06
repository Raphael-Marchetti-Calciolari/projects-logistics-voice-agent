from fastapi import APIRouter, Request, HTTPException
from database import supabase
from openai_client import openai_extractor
import json

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("/retell")
async def handle_retell_webhook(request: Request):
    """Handle webhooks from Retell AI"""
    try:
        body = await request.body()
        data = json.loads(body)
        
        event = data.get("event")
        call_data = data.get("call", {})
        call_id = call_data.get("call_id")
        
        print(f"\n{'='*60}")
        print(f"Webhook: {event} | Call: {call_id}")
        print(f"{'='*60}\n")
        
        if event == "call_started":
            result = supabase.table("call_logs")\
                .update({"call_status": "in_progress"})\
                .eq("retell_call_id", call_id)\
                .execute()
            print(f"Updated {len(result.data)} rows to in_progress")
        
        elif event == "call_ended":
            # Check if transcript is available in call_ended event
            transcript = call_data.get("transcript", "")
            
            if transcript:
                print(f"Transcript received in call_ended: {len(transcript)} characters")
                await process_transcript(call_id, transcript)
            else:
                # Just update status if no transcript yet
                result = supabase.table("call_logs")\
                    .update({"call_status": "completed"})\
                    .eq("retell_call_id", call_id)\
                    .execute()
                print(f"Updated {len(result.data)} rows to completed (no transcript yet)")
        
        elif event == "call_analyzed":
            transcript = call_data.get("transcript", "")
            
            if transcript:
                print(f"Transcript received in call_analyzed: {len(transcript)} characters")
                await process_transcript(call_id, transcript)
            else:
                print("Warning: No transcript in call_analyzed webhook")
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

async def process_transcript(call_id: str, transcript: str):
    """Process and store transcript with structured data extraction"""
    
    # Get scenario type from database
    call_info = supabase.table("call_logs")\
        .select("scenario_type")\
        .eq("retell_call_id", call_id)\
        .execute()
    
    if not call_info.data:
        print(f"Error: Call {call_id} not found in database")
        return
    
    scenario_type = call_info.data[0]["scenario_type"]
    print(f"Extracting structured data for scenario: {scenario_type}")
    
    # Extract structured data using OpenAI
    try:
        if scenario_type == "checkin":
            structured_data = await openai_extractor.extract_checkin_data(transcript)
        elif scenario_type == "emergency":
            structured_data = await openai_extractor.extract_emergency_data(transcript)
        else:
            print(f"Warning: Unknown scenario type: {scenario_type}")
            structured_data = None
        
        if structured_data:
            print(f"Extracted data: {json.dumps(structured_data, indent=2)}")
        
        # Update database with transcript and structured data
        supabase.table("call_logs")\
            .update({
                "raw_transcript": transcript,
                "structured_data": structured_data,
                "call_status": "completed"
            })\
            .eq("retell_call_id", call_id)\
            .execute()
        
        print(f"Stored transcript and structured data")
        
    except Exception as e:
        print(f"Error extracting structured data: {str(e)}")
        # Still save the transcript even if extraction fails
        supabase.table("call_logs")\
            .update({
                "raw_transcript": transcript,
                "call_status": "completed"
            })\
            .eq("retell_call_id", call_id)\
            .execute()
        print("Stored transcript only (extraction failed)")
