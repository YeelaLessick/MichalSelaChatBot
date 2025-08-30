from cryptography.fernet import Fernet
from azure.cosmos import CosmosClient, PartitionKey
import json

import openai

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

def finish_session(container, session_id, chat_history):
    """Finalizes the chat session and stores the chat history."""
    summary = summarize_conversation(chat_history)
    send_to_cosmos(container, session_id, chat_history)
    #clear_history(session_id) - DO we want to clear from here? do we need to?

def summarize_conversation(chat_history):
    """Summarizes the chat history."""
    # use an open ai agent to summarize the chat history based on a prompt we will provide in a variable
    prompt = f"Summarize the following chat history:\n{chat_history}"
    summary = call_openai_api(prompt)
    return summary

def call_openai_api(prompt):
    response = openai.Chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content

def send_to_cosmos(container, session_id, chat_history):
    #encrypted_history = cipher.encrypt(json.dumps(chat_history).encode())
    container.upsert_item({
        "id": session_id,
        "chat_history": chat_history # encrypted_history
    })

def test():
    pass
