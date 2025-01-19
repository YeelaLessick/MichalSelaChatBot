from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from azure.identity import ManagedIdentityCredential
import asyncio

# Initialize Flask app
app = Flask(__name__)

# Bot Framework Adapter
client_secret = os.getenv("BOT_CLIENT_SECRET")
if not client_secret:
    raise ValueError("BOT_CLIENT_SECRET is not set in the environment")
settings = BotFrameworkAdapterSettings(app_id="b7548fae-2a32-4390-a564-156fba07f887",app_password=client_secret)
adapter = BotFrameworkAdapter(settings)

# Debugging Managed Identity token
try:
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://graph.microsoft.com/.default")
    print("Managed Identity Token:", token.token)
except Exception as e:
    print(f"Failed to fetch Managed Identity Token: {e}")

# Echo Bot logic
async def echo_logic(turn_context: TurnContext):
    user_message = turn_context.activity.text
    await turn_context.send_activity(f"You said: {user_message}")

@app.route('/')
def index():
    return "Welcome to Michal Sela Bot!"

# Route to handle incoming messages
@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Invalid content type"}), 400

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    print(auth_header)
    #auth_header = None

    async def call_echo_logic(turn_context):
        await echo_logic(turn_context)

    try:
        task = adapter.process_activity(activity, auth_header, call_echo_logic)
        asyncio.run(task)  # Await the async task
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Run Flask app (use for local testing; ignored in Azure App Service)
if __name__ == "__main__":
    app.run(debug=True, port=3978)
