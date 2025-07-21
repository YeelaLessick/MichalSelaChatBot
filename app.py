from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from azure.identity import ManagedIdentityCredential
import asyncio
from michal_sela_chatbot import setup_chatbot, chat
import threading

# Initialize Flask app
app = Flask(__name__)

# Bot Framework Adapter
app_password = os.getenv("MicrosoftAppPassword")
app_id = os.getenv("MicrosoftAppId")
if not app_password:
    raise ValueError("MicrosoftAppPassword is not set in the environment")
if not app_id:
    raise ValueError("MicrosoftAppId is not set in the environment")
settings = BotFrameworkAdapterSettings(app_id=app_id, app_password=app_password)
adapter = BotFrameworkAdapter(settings)

setup_chatbot()

# Echo Bot logic
async def bot_logic(turn_context: TurnContext):
    """Handles messages from users, using a session-based chatbot."""
    session_id = turn_context.activity.conversation.id 
    user_message = turn_context.activity.text
    chatbot_response = await chat(session_id, user_message)
    print("chatbot_response: ", chatbot_response)
    await turn_context.send_activity(chatbot_response)

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
