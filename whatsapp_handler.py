import json
import uuid
from typing import Dict, Any, Optional
from azure.eventgrid import EventGridEvent
import asyncio
import traceback
from michal_sela_chatbot import chat, session_storage
from communication_client import send_whatsapp_message

# Maps clean phone number -> active session_id.
# Cleared automatically when a session ends (user sends "end" or background cleanup).
_phone_sessions: Dict[str, str] = {}

class WhatsAppEventHandler:
    """Handles Event Grid webhooks from Azure Communication Services for WhatsApp"""
    
    def __init__(self):
        """Initialize the WhatsApp event handler"""
        print("✅ WhatsApp Event Handler initialized")
    
    async def handle_webhook(self, request_headers: Dict[str, str], request_body: str) -> Dict[str, Any]:
        """
        Handle incoming Event Grid webhook
        
        Args:
            request_headers: HTTP request headers
            request_body: Raw JSON request body
        
        Returns:
            Dict containing response data
        """
        try:
            # Check event type from headers
            event_type = request_headers.get("aeg-event-type", "")
            
            if event_type == "SubscriptionValidation":
                return await self._handle_subscription_validation(request_body)
            elif event_type == "Notification":
                return await self._handle_notification(request_body)
            else:
                print(f"❌ Unknown event type: {event_type}")
                return {"error": f"Unknown event type: {event_type}", "status": 400}
                
        except Exception as e:
            print(f"❌ Error handling webhook: {e}")
            print(traceback.format_exc())
            return {"error": str(e), "status": 500}
    
    async def _handle_subscription_validation(self, request_body: str) -> Dict[str, Any]:
        """
        Handle Event Grid subscription validation
        
        Args:
            request_body: Raw JSON request body
        
        Returns:
            Dict containing validation response
        """
        try:
            # Parse the request body
            events = json.loads(request_body)
            if not isinstance(events, list) or len(events) == 0:
                return {"error": "Invalid validation request format", "status": 400}
            
            # Get the validation code from the first event
            first_event = events[0]
            validation_code = first_event.get("data", {}).get("validationCode")
            
            if not validation_code:
                return {"error": "Missing validation code", "status": 400}
            
            print(f"✅ Event Grid subscription validation successful")
            return {
                "validationResponse": validation_code,
                "status": 200
            }
            
        except Exception as e:
            print(f"❌ Error in subscription validation: {e}")
            return {"error": str(e), "status": 500}
    
    async def _handle_notification(self, request_body: str) -> Dict[str, Any]:
        """
        Handle Event Grid notification events
        
        Args:
            request_body: Raw JSON request body
        
        Returns:
            Dict containing processing status
        """
        try:
            # Parse the events
            events = json.loads(request_body)
            if not isinstance(events, list):
                return {"error": "Invalid notification format", "status": 400}
            
            processed_count = 0
            
            for event in events:
                try:
                    # Check if this is an advanced message received event
                    event_type = event.get("eventType", "")
                    if event_type.lower() == "microsoft.communication.advancedmessagereceived":
                        await self._process_whatsapp_message(event)
                        processed_count += 1
                    else:
                        print(f"ℹ️ Skipping event type: {event_type}")
                        
                except Exception as e:
                    print(f"❌ Error processing individual event: {e}")
                    print(f"❌ Event data: {json.dumps(event, indent=2)}")
                    continue
            
            print(f"✅ Processed {processed_count} WhatsApp events")
            return {"processed": processed_count, "status": 200}
            
        except Exception as e:
            print(f"❌ Error in notification handling: {e}")
            return {"error": str(e), "status": 500}
    
    async def _process_whatsapp_message(self, event: Dict[str, Any]) -> None:
        """
        Process a WhatsApp message event
        
        Args:
            event: Event Grid event containing WhatsApp message data
        """
        try:
            # Extract message data
            event_data = event.get("data", {})
            sender_phone = event_data.get("from", "")
            message_content = event_data.get("content", "")
            
            # Log the incoming message
            print(f"📱 WhatsApp message received from {sender_phone}: {message_content}")
            
            if not sender_phone or not message_content:
                print("❌ Missing sender phone or message content")
                return
            
            clean_phone = sender_phone.replace('+', '').replace('-', '').replace(' ', '')

            # Reuse existing session or create a new unique one
            session_id = _phone_sessions.get(clean_phone)
            if not session_id or session_id not in session_storage:
                session_id = f"whatsapp_{clean_phone}_{uuid.uuid4().hex[:8]}"
                _phone_sessions[clean_phone] = session_id

            # Process the message through the chatbot
            try:
                print(f"🤖 Processing message through chatbot for session: {session_id}")
                chatbot_response = await chat(session_id, message_content)
                print(f"✅ Chatbot response: {chatbot_response}")

                # If the session was ended (by user or background cleanup), remove from map
                if session_id not in session_storage:
                    _phone_sessions.pop(clean_phone, None)
                
                # Send the response back via WhatsApp
                success = await send_whatsapp_message(sender_phone, chatbot_response)
                
                if success:
                    print(f"✅ WhatsApp response sent successfully to {sender_phone}")
                else:
                    print(f"❌ Failed to send WhatsApp response to {sender_phone}")
                    
            except Exception as chatbot_error:
                print(f"❌ Error in chatbot processing: {chatbot_error}")
                print(traceback.format_exc())
                
                # Send fallback message
                fallback_message = "משהו השתבש אצלנו, נסי שוב עוד רגע 💜"
                await send_whatsapp_message(sender_phone, fallback_message)
                
        except Exception as e:
            print(f"❌ Error processing WhatsApp message: {e}")
            print(f"❌ Event data: {json.dumps(event, indent=2)}")
            print(traceback.format_exc())
    
    def handle_options_request(self, request_headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Handle OPTIONS request for webhook validation
        
        Args:
            request_headers: HTTP request headers
        
        Returns:
            Dict containing response headers and status
        """
        webhook_request_origin = request_headers.get("webhook-request-origin", "")
        
        response_headers = {
            "webhook-allowed-rate": "*",
            "webhook-allowed-origin": webhook_request_origin
        }
        
        print(f"✅ Handled OPTIONS request from origin: {webhook_request_origin}")
        
        return {
            "headers": response_headers,
            "status": 200
        }

# Global handler instance
_whatsapp_handler = None

def get_whatsapp_handler() -> WhatsAppEventHandler:
    """Get or create the global WhatsApp handler instance"""
    global _whatsapp_handler
    if _whatsapp_handler is None:
        _whatsapp_handler = WhatsAppEventHandler()
    return _whatsapp_handler

async def handle_whatsapp_webhook(request_headers: Dict[str, str], request_body: str) -> Dict[str, Any]:
    """
    Convenience function to handle WhatsApp webhook
    
    Args:
        request_headers: HTTP request headers
        request_body: Raw JSON request body
    
    Returns:
        Dict containing response data
    """
    handler = get_whatsapp_handler()
    return await handler.handle_webhook(request_headers, request_body)

def handle_whatsapp_options(request_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Convenience function to handle OPTIONS request
    
    Args:
        request_headers: HTTP request headers
    
    Returns:
        Dict containing response data
    """
    handler = get_whatsapp_handler()
    return handler.handle_options_request(request_headers)
