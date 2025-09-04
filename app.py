from flask import Flask, request, jsonify
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.core import TurnContext
from botbuilder.schema import Activity, ActivityTypes
import asyncio
import threading
import traceback
import os
from michal_sela_chatbot import setup_chatbot
from bot_framework_handler import handle_bot_framework_message
from whatsapp_handler import handle_whatsapp_webhook, handle_whatsapp_options
from config import DefaultConfig

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

@app.route('/')
def index():
    return "Welcome to Michal Sela Bot! 🤖💜"

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
            
            # Process webhook in a background thread to avoid timeout
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
