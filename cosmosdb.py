from cryptography.fernet import Fernet
from azure.cosmos import CosmosClient, PartitionKey
import json

# Encryption key should be securely stored and retrieved, e.g., from Azure Key Vault
encryption_key = Fernet.generate_key()  # TODO: Placeholder; in production use a securely stored key
cipher = Fernet(encryption_key)
container = None

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
    item = {
        "id": session_id,
        "SessionId": session_id,
        "Conversation": messages
    }
    print(f"Storing conversation for session {session_id} to Cosmos DB, item: {item}")
    container.upsert_item(item)

# check if the convestaion end message was sent
def is_end_conversation_message(last_message):
    if last_message.strip().lower() == "end":
        print("End of conversation detected.")
        return True
    return False

def test():
    pass
