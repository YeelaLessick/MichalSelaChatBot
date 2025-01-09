import streamlit as st
from michal_sela_chatbot import (  # Import your chatbot setup function
    chat,
    initialize_chatbot,
)

# Initialize the chatbot chain and conversation history in session state
if "chain_with_history" not in st.session_state:
    st.session_state["chain_with_history"] = initialize_chatbot()

if "messages" not in st.session_state:
    # Start with a greeting message from the assistant
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "היי, אני מיכל, הצ'אטבוט של מיכל סלע. איך אוכל לעזור לך היום?",
        }
    ]

# Streamlit app title
st.title("💬 Michal Sela Chatbot")

# Display chat messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# User input and chatbot response handling
if prompt := st.chat_input("Type your message here..."):
    # Append user's message to the chat history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Process the chatbot's response
    try:
        chatbot_response = chat(st.session_state["chain_with_history"], prompt)
    except Exception as e:
        chatbot_response = f"An error occurred: {str(e)}"

    # Append the assistant's response to the chat history
    st.session_state["messages"].append(
        {"role": "assistant", "content": chatbot_response}
    )
    st.chat_message("assistant").write(chatbot_response)
