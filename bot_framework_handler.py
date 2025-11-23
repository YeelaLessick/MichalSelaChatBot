import asyncio
import traceback
from botbuilder.core import TurnContext
from botbuilder.schema import Activity, ActivityTypes
from michal_sela_chatbot import chat

class BotFrameworkHandler:
    """Handles Bot Framework messages (Telegram, Web Chat, etc.)"""
    
    def __init__(self):
        """Initialize the Bot Framework handler"""
        print("✅ Bot Framework Handler initialized")
    
    async def handle_message(self, turn_context: TurnContext) -> None:
        """
        Handle incoming Bot Framework message
        
        Args:
            turn_context: Bot Framework turn context containing message data
        """
        try:
            # Extract session ID and message content
            session_id = turn_context.activity.conversation.id
            user_message = turn_context.activity.text
            
            # Skip processing if message is None or empty (e.g., system messages, typing indicators)
            if not user_message or not user_message.strip():
                print(f"⏭️ Skipping empty/None message from session {session_id}")
                return
            
            print(f"🤖 Bot Framework message received from session {session_id}: {user_message}")
            
            # Process the message through the chatbot
            chatbot_response = await chat(session_id, user_message)
            
            # Validate chatbot response before sending
            if not chatbot_response or not chatbot_response.strip():
                print(f"⚠️ Warning: Empty chatbot response for session {session_id}")
                chatbot_response = "משהו השתבש אצלנו, נסי שוב עוד רגע 💜"
            
            print(f"✅ Chatbot response: {chatbot_response}")

            # Send the response back through Bot Framework
            await turn_context.send_activity(
                Activity(
                    type=ActivityTypes.message,
                    text=chatbot_response,
                    text_format="plain"
                )
            )
            
            print(f"✅ Bot Framework response sent successfully to session {session_id}")
            
        except Exception as e:
            print(f"❌ Error in Bot Framework message handling: {e}")
            print(f"❌ Problematic message: {user_message if 'user_message' in locals() else 'N/A'}")
            print(traceback.format_exc())

            # Send Hebrew fallback message
            fallback_message = "משהו השתבש אצלנו, נסי שוב עוד רגע 💜"
            
            try:
                await turn_context.send_activity(
                    Activity(
                        type=ActivityTypes.message,
                        text=fallback_message,
                        text_format="plain"
                    )
                )
                print(f"✅ Fallback message sent to session {session_id if 'session_id' in locals() else 'unknown'}")
            except Exception as fallback_error:
                print(f"❌ Error sending fallback message: {fallback_error}")

# Global handler instance
_bot_framework_handler = None

def get_bot_framework_handler() -> BotFrameworkHandler:
    """Get or create the global Bot Framework handler instance"""
    global _bot_framework_handler
    if _bot_framework_handler is None:
        _bot_framework_handler = BotFrameworkHandler()
    return _bot_framework_handler

async def handle_bot_framework_message(turn_context: TurnContext) -> None:
    """
    Convenience function to handle Bot Framework message
    
    Args:
        turn_context: Bot Framework turn context
    """
    handler = get_bot_framework_handler()
    await handler.handle_message(turn_context)
