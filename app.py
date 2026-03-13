from flask import Flask, request, jsonify
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.core import TurnContext
from botbuilder.schema import Activity, ActivityTypes
import asyncio
import threading
import traceback
import os
import time
import logging
from michal_sela_chatbot import setup_chatbot, session_storage
from bot_framework_handler import handle_bot_framework_message
from whatsapp_handler import handle_whatsapp_webhook, handle_whatsapp_options
from config import DefaultConfig
from session_manager import cleanup_expired_sessions, get_active_session_count

# Configure logging - suppress verbose Azure SDK logs
logging.basicConfig(
    level=logging.WARNING,  # Only show WARNING and above for libraries
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set specific loggers to WARNING to reduce noise
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)

# Keep our app loggers at INFO level
logging.getLogger('michal_sela_chatbot').setLevel(logging.INFO)
logging.getLogger('session_manager').setLevel(logging.INFO)

print("Starting app")

# Initialize Flask app
app = Flask(__name__)

# Create configuration (instantiate the class)
CONFIG = DefaultConfig()

# Create adapter using CloudAdapter with ConfigurationBotFrameworkAuthentication
# This automatically handles User-Assigned Managed Identity based on environment variables
adapter = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# Initialize chatbot
setup_chatbot()

# Background job for session cleanup
def session_cleanup_job():
    """Background job that runs periodically to clean up expired sessions."""
    print(f"🧹 Session cleanup job started (runs every {CONFIG.SESSION_CLEANUP_INTERVAL_MINUTES} minutes, timeout: {CONFIG.SESSION_TIMEOUT_MINUTES} minutes)")
    
    # Run first cleanup immediately (don't wait)
    iteration = 0
    
    while True:
        try:
            iteration += 1
            
            # Get stats before cleanup
            sessions_before = get_active_session_count(session_storage)
            
            # Run cleanup
            print(f"🧹 Session cleanup #{iteration} started: checking {sessions_before} sessions")
            cleaned_count = cleanup_expired_sessions(session_storage, CONFIG.SESSION_TIMEOUT_MINUTES)
            
            # Get stats after cleanup
            sessions_after = get_active_session_count(session_storage)
            
            if cleaned_count > 0:
                print(f"✅ Session cleanup #{iteration} completed: {cleaned_count} sessions removed, {sessions_after} active sessions remaining")
            else:
                print(f"✅ Session cleanup #{iteration} completed: No expired sessions found, {sessions_after} active sessions")
            
            # Wait for the configured interval before next cleanup
            print(f"⏰ Next cleanup in {CONFIG.SESSION_CLEANUP_INTERVAL_MINUTES} minutes...")
            time.sleep(CONFIG.SESSION_CLEANUP_INTERVAL_MINUTES * 60)
                
        except Exception as e:
            print(f"❌ Error in session cleanup job: {e}")
            print(traceback.format_exc())
            # Wait before retrying after error
            time.sleep(60)

# Start session cleanup background job as daemon thread
cleanup_thread = threading.Thread(target=session_cleanup_job, daemon=True)
cleanup_thread.start()
print(f"✅ Background cleanup thread started successfully")

@app.route('/')
def index():
    return "Welcome to Michal Sela Bot! 🤖💜"

@app.route('/api/debug/sessions')
def debug_sessions():
    """Debug endpoint to check session status and cleanup configuration."""
    from datetime import datetime
    from session_manager import get_session_statistics
    
    stats = get_session_statistics(session_storage)
    
    # Get detailed session info
    session_details = []
    current_time = datetime.now()
    for session_id, session_data in session_storage.items():
        last_modified = session_data.get("last_modified")
        created_at = session_data.get("created_at")
        inactive_minutes = int((current_time - last_modified).total_seconds() / 60) if last_modified else None
        
        session_details.append({
            "session_id": session_id,
            "created_at": created_at.isoformat() if created_at else None,
            "last_modified": last_modified.isoformat() if last_modified else None,
            "inactive_minutes": inactive_minutes,
            "message_count": len(session_data.get("history").messages) if session_data.get("history") else 0,
            "will_expire": inactive_minutes >= CONFIG.SESSION_TIMEOUT_MINUTES if inactive_minutes else False
        })
    
    return jsonify({
        "config": {
            "cleanup_interval_minutes": CONFIG.SESSION_CLEANUP_INTERVAL_MINUTES,
            "session_timeout_minutes": CONFIG.SESSION_TIMEOUT_MINUTES
        },
        "statistics": stats,
        "sessions": session_details,
        "cleanup_thread_alive": cleanup_thread.is_alive()
    })

# Route to handle Bot Framework messages (Telegram, Web Chat, etc.)
@app.route("/api/messages", methods=["POST"])
def messages():
    print("📨 Received Bot Framework message")
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Invalid content type"}), 400

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_bot_framework_logic(turn_context):
        await handle_bot_framework_message(turn_context)

    # Run bot processing in a background thread
    thread = threading.Thread(target=asyncio.run, args=(adapter.process_activity(auth_header, activity, call_bot_framework_logic),))
    thread.start()

    # Return response immediately to avoid timeout
    return jsonify({"status": "Processing"}), 202

# Route to handle WhatsApp webhook (Event Grid)
@app.route("/api/whatsapp/webhook", methods=["POST", "OPTIONS"])
def whatsapp_webhook():
    print("📱 Received WhatsApp webhook request")
    
    # Handle OPTIONS request for webhook validation
    if request.method == "OPTIONS":
        try:
            request_headers = {key.lower(): value for key, value in request.headers.items()}
            response_data = handle_whatsapp_options(request_headers)
            
            response = jsonify({"status": "ok"})
            
            # Add response headers if provided
            if "headers" in response_data:
                for header_name, header_value in response_data["headers"].items():
                    response.headers[header_name] = header_value
            
            return response, response_data.get("status", 200)
            
        except Exception as e:
            print(f"❌ Error handling OPTIONS request: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Handle POST request (actual webhook)
    if request.method == "POST":
        try:
            # Check content type
            if "application/json" not in request.headers.get("Content-Type", ""):
                return jsonify({"error": "Invalid content type"}), 400
            
            # Get request data
            request_headers = {key.lower(): value for key, value in request.headers.items()}
            request_body = request.get_data(as_text=True)
            
            # Check if this is a subscription validation request
            event_type = request_headers.get("aeg-event-type", "")
            
            if event_type == "SubscriptionValidation":
                # Handle validation synchronously - Event Grid needs immediate response
                print("🔐 Handling Event Grid subscription validation")
                async def validate():
                    return await handle_whatsapp_webhook(request_headers, request_body)
                
                result = asyncio.run(validate())
                
                # Return validation response immediately
                if "validationResponse" in result:
                    print(f"✅ Returning validation response")
                    return jsonify({"validationResponse": result["validationResponse"]}), 200
                else:
                    print(f"❌ Validation failed: {result}")
                    return jsonify({"error": result.get("error", "Validation failed")}), result.get("status", 400)
            
            else:
                # Handle notifications asynchronously to avoid timeout
                async def process_webhook():
                    try:
                        result = await handle_whatsapp_webhook(request_headers, request_body)
                        print(f"✅ WhatsApp webhook processed: {result}")
                    except Exception as e:
                        print(f"❌ Error processing WhatsApp webhook: {e}")
                        print(traceback.format_exc())
                
                # Start background processing
                thread = threading.Thread(target=asyncio.run, args=(process_webhook(),))
                thread.start()
                
                # Return immediate response to Event Grid
                return jsonify({"status": "Processing"}), 202
            
        except Exception as e:
            print(f"❌ Error in WhatsApp webhook handler: {e}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

# Run Flask app (use for local testing; ignored in Azure App Service)
if __name__ == "__main__":
    app.run(debug=True, port=3978)
