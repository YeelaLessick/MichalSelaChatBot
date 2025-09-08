#!/usr/bin/env python3
"""
WhatsApp Configuration Test Script
This script validates your WhatsApp integration configuration.
"""

import os
from dotenv import load_dotenv
import sys

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔧 Testing Environment Variables...")
    
    load_dotenv()
    
    required_vars = [
        "COMMUNICATION_SERVICES_CONNECTION_STRING",
        "WHATSAPP_CHANNEL_REGISTRATION_ID",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "DEPLOYMENT_NAME",
        "MicrosoftAppId",
        "MicrosoftAppPassword"
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif "your_" in value.lower() or "here" in value.lower():
            placeholder_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
    
    if placeholder_vars:
        print(f"\n⚠️  Variables with placeholder values (need to be updated):")
        for var in placeholder_vars:
            print(f"   - {var}")
    
    return len(missing_vars) == 0 and len(placeholder_vars) == 0

def test_dependencies():
    """Test if required Python packages are installed"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        "azure.communication.messages",
        "azure.eventgrid",
        "flask",
        "botbuilder.core",
        "langchain_openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: Missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages. Install with:")
        print(f"pip install azure-communication-messages azure-messaging-eventgrid")
    
    return len(missing_packages) == 0

def test_communication_services():
    """Test Azure Communication Services connection"""
    print("\n🔗 Testing Communication Services Connection...")
    
    try:
        from azure.communication.messages import NotificationMessagesClient
        
        connection_string = os.getenv("COMMUNICATION_SERVICES_CONNECTION_STRING")
        if not connection_string or "your_" in connection_string.lower():
            print("⚠️  Communication Services connection string not configured")
            return False
        
        # Try to create client (doesn't make actual calls)
        client = NotificationMessagesClient.from_connection_string(connection_string)
        print("✅ Communication Services client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Communication Services connection failed: {e}")
        return False

def test_chatbot_logic():
    """Test if chatbot logic can be imported"""
    print("\n🤖 Testing Chatbot Logic...")
    
    try:
        from michal_sela_chatbot import setup_chatbot
        print("✅ Chatbot module imported successfully")
        
        # Try to setup chatbot
        setup_chatbot()
        print("✅ Chatbot setup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot setup failed: {e}")
        return False

def test_app_endpoints():
    """Test if Flask app can be imported"""
    print("\n🌐 Testing Flask App...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Check if routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        required_routes = ["/", "/api/messages", "/api/whatsapp/webhook"]
        for route in required_routes:
            if route in routes:
                print(f"✅ Route {route}: Registered")
            else:
                print(f"❌ Route {route}: Missing")
        
        return all(route in routes for route in required_routes)
        
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 WhatsApp Integration Configuration Test\n")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Dependencies", test_dependencies),
        ("Communication Services", test_communication_services),
        ("Chatbot Logic", test_chatbot_logic),
        ("Flask App", test_app_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your WhatsApp integration is ready.")
        print("\nNext steps:")
        print("1. Deploy your code to Azure App Service")
        print("2. Create Event Grid subscription in Communication Services")
        print("3. Test with a WhatsApp message")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nRefer to WHATSAPP_SETUP_GUIDE.md for detailed instructions.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
