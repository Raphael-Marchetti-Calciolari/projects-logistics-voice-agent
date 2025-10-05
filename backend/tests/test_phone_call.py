import asyncio
import os
from dotenv import load_dotenv
from retell import AsyncRetell

load_dotenv()

async def test_phone_setup():
    """Test phone number configuration"""
    
    client = AsyncRetell(api_key=os.getenv("RETELL_API_KEY"))
    from_number = os.getenv("RETELL_FROM_NUMBER")
    
    print("=" * 60)
    print("TESTING PHONE SETUP")
    print("=" * 60)
    
    print(f"\n📱 From number in .env: {from_number}")
    
    # Try to list phone numbers
    print("\n1️⃣ Checking Retell phone numbers...")
    try:
        phone_numbers = await client.phone_number.list()
        print(f"   Found {len(phone_numbers)} phone numbers in Retell:")
        for phone in phone_numbers:
            print(f"   - {phone.phone_number}")
            if phone.phone_number == from_number:
                print(f"     ✅ Matches RETELL_FROM_NUMBER")
    except Exception as e:
        print(f"   ⚠️ Could not list phone numbers: {e}")
        print("\n   NOTE: You may need to purchase a phone number in Retell dashboard:")
        print("   https://beta.retellai.com/dashboard/phone-numbers")

if __name__ == "__main__":
    asyncio.run(test_phone_setup())