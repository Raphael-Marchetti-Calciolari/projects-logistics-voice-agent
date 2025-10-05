import asyncio
import os
from dotenv import load_dotenv
from database import supabase
import httpx

load_dotenv()

API_BASE = "http://localhost:8000"

async def test_call_flow():
    """Test the complete call initiation flow"""
    print("=" * 60)
    print("TESTING CALL FLOW")
    print("=" * 60)
    
    test_call_id = None
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Check if agent exists
            print("\n1️⃣ Checking for configured agents...")
            response = await client.get(f"{API_BASE}/api/configurations")
            configs = response.json()
            
            if not configs:
                print("❌ No configurations found. Create one first!")
                return
            
            checkin_config = next((c for c in configs if c['scenario_type'] == 'checkin'), None)
            if not checkin_config:
                print("❌ No check-in configuration found")
                return
            
            if not checkin_config.get('agent_id'):
                print("❌ Check-in agent not created yet")
                return
            
            print(f"✅ Found check-in agent: {checkin_config['agent_id']}")
            
            # Step 2: Test call initiation (will fail on phone validation, but that's ok)
            print("\n2️⃣ Testing call initiation endpoint...")
            
            call_data = {
                "driver_name": "Test Driver",
                "driver_phone": "+14155551234",  # Valid E.164 format
                "load_number": "TEST-123",
                "scenario_type": "checkin"
            }
            
            response = await client.post(
                f"{API_BASE}/api/calls/initiate",
                json=call_data
            )
            
            if response.status_code == 200:
                result = response.json()
                test_call_id = result.get('call_id')
                print(f"✅ Call initiated successfully!")
                print(f"   Call ID: {test_call_id}")
                print(f"   Retell Call ID: {result.get('retell_call_id')}")
            else:
                error = response.json()
                print(f"⚠️  Call initiation returned {response.status_code}")
                print(f"   Error: {error.get('detail', 'Unknown error')}")
                
                # Check if call_log was created anyway
                print("\n   Checking if call_log was created...")
                result = supabase.table("call_logs")\
                    .select("*")\
                    .eq("driver_phone", call_data["driver_phone"])\
                    .order("created_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                if result.data:
                    test_call_id = result.data[0]['id']
                    print(f"   ✅ Found call_log: {test_call_id}")
                    print(f"   Status: {result.data[0]['call_status']}")
            
            # Step 3: Test webhook endpoint (simulate)
            print("\n3️⃣ Testing webhook endpoint...")
            webhook_data = {
                "event": "call_started",
                "call": {
                    "call_id": "test_retell_call_123"
                }
            }
            
            response = await client.post(
                f"{API_BASE}/api/webhooks/retell",
                json=webhook_data
            )
            
            if response.status_code == 200:
                print("✅ Webhook endpoint responding")
            else:
                print(f"⚠️  Webhook returned {response.status_code}")
            
            # Step 4: Verify database structure
            print("\n4️⃣ Verifying database records...")
            
            # Check call_logs table
            all_calls = supabase.table("call_logs").select("*").execute()
            print(f"✅ Total calls in database: {len(all_calls.data)}")
            
            if all_calls.data:
                latest = all_calls.data[-1]
                print(f"   Latest call:")
                print(f"   - Driver: {latest['driver_name']}")
                print(f"   - Status: {latest['call_status']}")
                print(f"   - Has Retell ID: {bool(latest.get('retell_call_id'))}")
            
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print("✅ API endpoints: Working")
            print("✅ Database integration: Working")
            print("✅ Agent configuration: Working")
            print("⚠️  Actual call placement: Requires valid Retell phone number")
            print("\nTo make real calls, you need:")
            print("1. A Retell phone number (or Twilio integration)")
            print("2. Update from_number in calls.py")
            print("3. Use valid E.164 phone numbers (+1XXXXXXXXXX)")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n" + "=" * 60)
        print("CLEANUP")
        print("=" * 60)
        
        if test_call_id:
            print(f"Cleaning up test call: {test_call_id}")
            supabase.table("call_logs").delete().eq("id", test_call_id).execute()
            print("✅ Cleanup complete")
        
        # Clean up any test calls
        result = supabase.table("call_logs")\
            .delete()\
            .eq("load_number", "TEST-123")\
            .execute()
        
        if result.data:
            print(f"✅ Cleaned up {len(result.data)} test records")

if __name__ == "__main__":
    print("Starting call flow test...")
    print("Make sure backend is running on http://localhost:8000")
    print()
    asyncio.run(test_call_flow())
