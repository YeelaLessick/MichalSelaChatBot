from cryptography.fernet import Fernet
from azure.cosmos import CosmosClient, PartitionKey
import json

# Encryption key should be securely stored and retrieved, e.g., from Azure Key Vault
encryption_key = Fernet.generate_key()  # TODO: Placeholder; in production use a securely stored key
cipher = Fernet(encryption_key)

def connect_to_cosmos(endpoint, key, database_name, container_name):
    client = CosmosClient(endpoint, key)
    database = client.create_database_if_not_exists(id=database_name)
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id")
    )
    return container

# send all the conversation messages to cosmos db as is, no encryption
def send_convessation_to_cosmos(container, session_id, messages):
    item = {
        "id": session_id,
        "messages": messages
    }
    container.upsert_item(item)

# check if the convestaion end message was sent
def is_end_conversation_message(last_message):
    if last_message.strip().lower() == "end":
        print("End of conversation detected.")
        return True
    return False

def test():
    pass
