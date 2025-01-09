from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

# Initialize Flask app
app = Flask(__name__)

# Bot Framework Adapter
settings = BotFrameworkAdapterSettings(app_id="74eb9820-0f07-4a5d-9078-7e29eb3e8f59", app_password=None )
adapter = BotFrameworkAdapter(settings)

# Echo Bot logic
async def echo_logic(turn_context: TurnContext):
    user_message = turn_context.activity.text
    await turn_context.send_activity(f"You said: {user_message}")

# Route to handle incoming messages
@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Invalid content type"}), 400

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_echo_logic(turn_context):
        await echo_logic(turn_context)

    try:
        task = adapter.process_activity(activity, auth_header, call_echo_logic)
        task.result()  # Wait for task to complete
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Run Flask app (use for local testing; ignored in Azure App Service)
if __name__ == "__main__":
    app.run(debug=True, port=3978)