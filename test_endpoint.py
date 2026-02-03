"""
Test script for Honeypot API
Tests all endpoints and validates responses
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')  # Change this when deployed
API_KEY = os.getenv('API_KEY', 'your-api-key-here')  # Loaded from .env file

# Test cases
test_messages = [
    {
        "name": "Prize Scam",
        "message_id": "msg_001",
        "sender": "scammer_prize",
        "message": "Congratulations! You have won ₹50,000 in our lucky draw! To claim your prize, please share your bank account number and IFSC code. Call us at 9876543210 or visit http://fake-lottery.com"
    },
    {
        "name": "Banking Fraud",
        "message_id": "msg_002",
        "sender": "scammer_bank",
        "message": "URGENT! Your SBI account has been blocked due to suspicious activity. Update your KYC immediately by sharing OTP and card details. Contact: support@fake-sbi.com"
    },
    {
        "name": "Payment Scam",
        "message_id": "msg_003",
        "sender": "scammer_payment",
        "message": "I accidentally sent ₹5000 to your PhonePe. Please refund to my UPI: scammer@paytm. This is urgent, please help!"
    },
    {
        "name": "Investment Fraud",
        "message_id": "msg_004",
        "sender": "scammer_invest",
        "message": "Guaranteed 30% monthly returns! Join our exclusive Bitcoin investment program. Minimum ₹10,000. Limited slots! Register at http://fake-invest.com"
    },
    {
        "name": "Follow-up Message (Prize Scam)",
        "message_id": "msg_005",
        "sender": "scammer_prize",
        "message": "Please provide details to claim your prize. Our account number is 1234567890, IFSC: SBIN0001234. You can also pay via UPI: winner@sbi"
    }
]


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check Endpoint")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_authentication():
    """Test API authentication"""
    print("\n" + "="*50)
    print("Testing Authentication")
    print("="*50)
    
    # Test without API key
    print("\n1. Testing without API key...")
    try:
        response = requests.post(f"{BASE_URL}/api/honeypot", json={
            "message_id": "test_001",
            "sender": "test",
            "message": "test message"
        })
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected request without API key")
        else:
            print("❌ Should have rejected request without API key")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with wrong API key
    print("\n2. Testing with wrong API key...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/honeypot",
            headers={"X-API-Key": "wrong-key"},
            json={
                "message_id": "test_001",
                "sender": "test",
                "message": "test message"
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 403:
            print("✅ Correctly rejected request with wrong API key")
        else:
            print("❌ Should have rejected request with wrong API key")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_honeypot_endpoint(test_case):
    """Test honeypot endpoint with a specific test case"""
    print(f"\n{'='*50}")
    print(f"Testing: {test_case['name']}")
    print(f"{'='*50}")
    
    payload = {
        "message_id": test_case["message_id"],
        "sender": test_case["sender"],
        "message": test_case["message"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/honeypot",
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = [
                'message_id', 'is_scam', 'confidence', 
                'persona_response', 'extracted_intelligence',
                'conversation_stage', 'next_action'
            ]
            
            missing_fields = [f for f in required_fields if f not in data]
            
            if not missing_fields:
                print(f"\n✅ {test_case['name']} - Test passed!")
                print(f"   - Scam detected: {data['is_scam']}")
                print(f"   - Confidence: {data['confidence']}")
                print(f"   - Stage: {data['conversation_stage']}")
                
                # Show extracted intelligence
                intel = data['extracted_intelligence']
                if any(intel.values()):
                    print(f"\n   Intelligence Extracted:")
                    for key, value in intel.items():
                        if value:
                            print(f"   - {key}: {value}")
                
                return True
            else:
                print(f"\n❌ Missing fields in response: {missing_fields}")
                return False
        else:
            print(f"\n❌ {test_case['name']} - Test failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_conversation_flow():
    """Test multi-turn conversation"""
    print(f"\n{'='*50}")
    print("Testing Multi-Turn Conversation Flow")
    print(f"{'='*50}")
    
    conversation = [
        {
            "name": "Conversation Turn 1",
            "message_id": "conv_001",
            "sender": "scammer_conversation",
            "message": "You won ₹1 lakh! Claim now!"
        },
        {
            "name": "Conversation Turn 2",
            "message_id": "conv_002",
            "sender": "scammer_conversation",
            "message": "Share your account number to receive the prize money"
        },
        {
            "name": "Conversation Turn 3",
            "message_id": "conv_003",
            "sender": "scammer_conversation",
            "message": "Transfer to account 9876543210987, IFSC HDFC0001234, or UPI scam@oksbi"
        }
    ]
    
    for i, msg in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        test_honeypot_endpoint(msg)


def run_all_tests():
    """Run all tests"""
    print("\n" + "🎯"*25)
    print("HONEYPOT API TEST SUITE")
    print("🎯"*25)
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n⚠️ Server is not running! Start the server first:")
        print("   python app.py")
        return
    
    # Test 2: Authentication
    test_authentication()
    
    # Test 3: Individual test cases
    print("\n" + "🔍"*25)
    print("TESTING SCAM DETECTION")
    print("🔍"*25)
    
    passed = 0
    failed = 0
    
    for test_case in test_messages:
        if test_honeypot_endpoint(test_case):
            passed += 1
        else:
            failed += 1
    
    # Test 4: Conversation flow
    test_conversation_flow()
    
    # Summary
    print("\n" + "📊"*25)
    print("TEST SUMMARY")
    print("📊"*25)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("\n" + "="*50)


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║      HONEYPOT API ENDPOINT TESTER                 ║
    ║      National Level Hackathon                     ║
    ╚═══════════════════════════════════════════════════╝
    
    Make sure:
    1. Server is running (python app.py)
    2. API_KEY in this file matches your .env
    3. BASE_URL points to your server
    """)
    
    input("Press Enter to start tests...")
    run_all_tests()