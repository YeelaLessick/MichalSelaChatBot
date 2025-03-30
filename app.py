from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from azure.identity import ManagedIdentityCredential
import asyncio
from michal_sela_chatbot import setup_chatbot, chat
import threading
from botbuilder.core import MessageFactory, InputHints

# Initialize Flask app
app = Flask(__name__)

# Bot Framework Adapter
#client_secret = os.getenv("BOT_CLIENT_SECRET")
client_secret = "-MJ8Q~mntwp0FCUncWjMWJ16qBolrfHxgKZ3qbHi"
if not client_secret:
    raise ValueError("BOT_CLIENT_SECRET is not set in the environment")
settings = BotFrameworkAdapterSettings(app_id="b7548fae-2a32-4390-a564-156fba07f887",app_password=client_secret)
adapter = BotFrameworkAdapter(settings)

setup_chatbot()

# Echo Bot logic
async def bot_logic(turn_context: TurnContext):
    """Handles messages from users, using a session-based chatbot."""
    session_id = turn_context.activity.conversation.id 
    user_message = turn_context.activity.text
    chatbot_response = await chat(session_id, user_message)
    print("chatbot_response: ", chatbot_response)
    await turn_context.send_activity(chatbot_response, chatbot_response, InputHints.ignoring_input)

@app.route('/')
def index():
    return "Welcome to Michal Sela Bot!"

# Route to handle incoming messages
@app.route("/api/messages", methods=["POST"])
def messages():
    print("Received message")
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Invalid content type"}), 400

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_echo_logic(turn_context):
        await bot_logic(turn_context)

     # ✅ Run bot processing in a background thread
    thread = threading.Thread(target=asyncio.run, args=(adapter.process_activity(activity, auth_header, call_echo_logic),))
    thread.start()

    # ✅ Return response immediately to avoid timeout
    return jsonify({"status": "Processing"}), 202

# Run Flask app (use for local testing; ignored in Azure App Service)
if __name__ == "__main__":
    app.run(debug=True, port=3978)
