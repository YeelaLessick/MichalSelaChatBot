from cryptography.fernet import Fernet
from azure.cosmos import CosmosClient, PartitionKey
import json

# Encryption key should be securely stored and retrieved, e.g., from Azure Key Vault
encryption_key = Fernet.generate_key()  # TODO: Placeholder; in production use a securely stored key
cipher = Fernet(encryption_key)
container = None

def messages_to_json(messages):
    """Convert list of BaseMessage objects to JSON-serializable list."""
    if not messages:
        return []
    
    serialized = []
    for msg in messages:
        try:
            # Handle both BaseMessage objects and dicts
            if isinstance(msg, dict):
                serialized.append(msg)
            else:
                # It's a BaseMessage object
                serialized.append({
                    "type": str(msg.type) if hasattr(msg, 'type') else "unknown",
                    "content": str(msg.content) if hasattr(msg, 'content') else "",
                    "additional_kwargs": dict(msg.additional_kwargs) if hasattr(msg, 'additional_kwargs') else {}
                })
        except Exception as e:
            print(f"⚠️  Error serializing message: {str(e)}")
            serialized.append({"type": "error", "content": str(msg)})
    
    return serialized

def connect_to_cosmos(connection_string, database_name, container_name):
    if connection_string is None or database_name is None or container_name is None:
        raise ValueError("Cosmos DB connection parameters must be provided.")
    global container
    client = CosmosClient.from_connection_string(connection_string)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

# send all the conversation messages to cosmos db as is, no encryption
def send_convessation_to_cosmos(session_id, messages):
    global container
    if container is None:
        raise Exception("Cosmos DB container is not connected.")
    try:
        item = {
            "id": session_id,
            "SessionId": session_id,
            "Conversation": messages_to_json(messages)
        }
        print(f"Storing conversation for session {session_id} to Cosmos DB")
        container.upsert_item(item)
        print(f"✅ Conversation stored successfully for session {session_id}")
    except Exception as e:
        print(f"❌ Error storing conversation to Cosmos DB: {str(e)}")

# check if the convestaion end message was sent
def is_end_conversation_message(last_message):
    if last_message.strip().lower() == "end":
        print("End of conversation detected.")
        return True
    return False

def test():
    pass
