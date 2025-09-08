#!/usr/bin/env python3
"""
Test script to simulate Event Grid validation request
"""

import json
import requests
from typing import Dict, Any

def create_validation_request() -> Dict[str, Any]:
    """Create a mock Event Grid validation request"""
    return {
        "headers": {
            "aeg-event-type": "SubscriptionValidation",
            "content-type": "application/json"
        },
        "body": json.dumps([{
            "id": "2d1781af-3a4c-4d7c-bd0c-e34b19da4e66",
            "topic": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/rg-name/providers/Microsoft.Communication/CommunicationServices/communication-service-name",
            "subject": "",
            "data": {
                "validationCode": "512d38b6-c7b8-40c8-89fe-f46f9e9622b6",
                "validationUrl": "https://rp-eastus2.eventgrid.azure.net:553/eventsubscriptions/estest/validate?id=512d38b6-c7b8-40c8-89fe-f46f9e9622b6&t=2018-04-26T20:30:54.4538837Z&apiVersion=2018-05-01-preview&token=1A1A1A1A"
            },
            "eventType": "Microsoft.EventGrid.SubscriptionValidationEvent",
            "eventTime": "2018-01-25T22:12:19.4556811Z",
            "metadataVersion": "1",
            "dataVersion": "1"
        }])
    }

def test_validation_endpoint():
    """Test the validation endpoint"""
    print("🧪 Testing Event Grid validation endpoint...")
    
    # Create validation request
    validation_request = create_validation_request()
    
    # Test URL (adjust if running on different port)
    url = "http://localhost:3978/api/whatsapp/webhook"
    
    try:
        response = requests.post(
            url,
            headers=validation_request["headers"],
            data=validation_request["body"],
            timeout=10
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        print(f"✅ Response Body: {response.text}")
        
        # Check if response contains validationResponse
        if response.status_code == 200:
            try:
                response_json = response.json()
                if "validationResponse" in response_json:
                    print("✅ SUCCESS: Validation response found!")
                    print(f"✅ Validation Code: {response_json['validationResponse']}")
                    return True
                else:
                    print("❌ FAIL: No validationResponse in response")
                    return False
            except Exception as e:
                print(f"❌ FAIL: Could not parse JSON response: {e}")
                return False
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure Flask app is running on port 3978")
        print("💡 Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Event Grid Validation Test")
    print("=" * 50)
    
    success = test_validation_endpoint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test PASSED! Validation endpoint works correctly.")
        print("✅ Ready to create Event Grid subscription in Azure.")
    else:
        print("❌ Test FAILED! Check the endpoint implementation.")
    
    print("\nTo run this test:")
    print("1. Start Flask app: python app.py")
    print("2. Run this test: python test_validation.py")
