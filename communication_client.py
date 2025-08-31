import os
from typing import List
from azure.communication.messages import NotificationMessagesClient
from azure.communication.messages.models import TextNotificationContent
import asyncio
import traceback

class WhatsAppCommunicationClient:
    """Handles Azure Communication Services for WhatsApp messaging"""
    
    def __init__(self):
        """Initialize the Communication Services client"""
        self.connection_string = os.getenv("COMMUNICATION_SERVICES_CONNECTION_STRING")
        self.channel_registration_id = os.getenv("WHATSAPP_CHANNEL_REGISTRATION_ID")
        
        if not self.connection_string:
            raise ValueError("COMMUNICATION_SERVICES_CONNECTION_STRING is not set in environment")
        
        if not self.channel_registration_id:
            raise ValueError("WHATSAPP_CHANNEL_REGISTRATION_ID is not set in environment")
        
        # Initialize the client
        self.client = NotificationMessagesClient.from_connection_string(self.connection_string)
        print("✅ WhatsApp Communication Client initialized")
    
    async def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """
        Send a WhatsApp message to a specific phone number
        
        Args:
            phone_number: The recipient's phone number (e.g., "+1234567890")
            message: The text message to send
        
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Ensure phone number is in correct format
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number.lstrip('+')
            
            recipient_list = [phone_number]
            
            # Create text notification content
            text_content = TextNotificationContent(
                channel_registration_id=self.channel_registration_id,
                to=recipient_list,
                content=message
            )
            
            # Send the message
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.send(text_content)
            )
            
            print(f"✅ WhatsApp message sent to {phone_number}")
            print(f"📤 Message: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending WhatsApp message to {phone_number}: {e}")
            print(f"❌ Message content: {message}")
            print(traceback.format_exc())
            return False
    
    def validate_configuration(self) -> bool:
        """
        Validate that all required configuration is present
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not self.connection_string:
            print("❌ Missing COMMUNICATION_SERVICES_CONNECTION_STRING")
            return False
        
        if not self.channel_registration_id:
            print("❌ Missing WHATSAPP_CHANNEL_REGISTRATION_ID")
            return False
        
        try:
            # Test client initialization
            test_client = NotificationMessagesClient.from_connection_string(self.connection_string)
            print("✅ Communication Services configuration is valid")
            return True
        except Exception as e:
            print(f"❌ Invalid Communication Services configuration: {e}")
            return False


# Global client instance (initialized once)
_whatsapp_client = None

def get_whatsapp_client() -> WhatsAppCommunicationClient:
    """Get or create the global WhatsApp client instance"""
    global _whatsapp_client
    if _whatsapp_client is None:
        _whatsapp_client = WhatsAppCommunicationClient()
    return _whatsapp_client

async def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """
    Convenience function to send a WhatsApp message
    
    Args:
        phone_number: The recipient's phone number
        message: The text message to send
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    client = get_whatsapp_client()
    return await client.send_whatsapp_message(phone_number, message)
