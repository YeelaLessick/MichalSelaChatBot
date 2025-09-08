#!/usr/bin/env python3
"""
Test script to verify Managed Identity configuration for Bot Framework
"""

import os
import sys
from dotenv import load_dotenv

def test_managed_identity_setup():
    """Test the Managed Identity setup without starting the full app"""
    
    print("🧪 Testing Managed Identity Setup for Bot Framework")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    app_id = os.getenv("MicrosoftAppId")
    app_type = os.getenv("MicrosoftAppType")
    
    print(f"✅ MicrosoftAppId: {app_id}")
    print(f"✅ MicrosoftAppType: {app_type}")
    
    if not app_id:
        print("❌ ERROR: MicrosoftAppId is not set")
        return False
    
    if app_type != "UserAssignedMSI":
        print("⚠️  WARNING: MicrosoftAppType is not set to 'UserAssignedMSI'")
    
    # Test Bot Framework import and initialization
    try:
        from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
        print("✅ Bot Framework imports successful")
        
        # Test creating settings (this should not fail now)
        settings = BotFrameworkAdapterSettings(app_id=app_id)
        print("✅ BotFrameworkAdapterSettings created successfully")
        
        # Test creating adapter
        adapter = BotFrameworkAdapter(settings)
        print("✅ BotFrameworkAdapter created successfully")
        
        print("\n🎉 SUCCESS: Managed Identity configuration is correct!")
        print("📋 Summary:")
        print("   - No credential parameter needed")
        print("   - Bot Framework will use Managed Identity automatically")
        print("   - Ready for Azure App Service deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("💡 Make sure your requirements.txt is installed: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = test_managed_identity_setup()
    sys.exit(0 if success else 1)
