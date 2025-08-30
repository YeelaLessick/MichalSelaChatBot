import json
import os
from typing import List
import pandas as pd
from azure.storage.blob import BlobServiceClient
from bidi.algorithm import get_display
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import AzureChatOpenAI
import re
import asyncio
from cosmosdb import finish_session, connect_to_cosmos
from utils import format_examples_and_communication, sheet_to_json

# Global storage for chatbot instance
STORAGE = {}
CHAIN = None  # Will be initialized once
CONTAINER = None

def setup_chatbot():
    """Initializes chatbot components once at startup."""
    global CHAIN
    global CONTAINER

    # Load environment variables
    load_dotenv(override=True)
    env_vars = {
        "azure_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_name": os.getenv("DEPLOYMENT_NAME"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "cosmos_endpoint": os.getenv("COSMOS_DB_ENDPOINT"),
        "cosmos_key": os.getenv("COSMOS_DB_KEY"),
        "cosmos_db_name": os.getenv("COSMOS_DB_DATABASE"),
        "cosmos_container_name": os.getenv("COSMOS_DB_CONTAINER")
    }

    CONTAINER = connect_to_cosmos(
        endpoint=env_vars["cosmos_endpoint"],
        key=env_vars["cosmos_key"],
        database_name=env_vars["cosmos_db_name"],
        container_name=env_vars["cosmos_container_name"]
    )

    # Load data for examples and communication centers
    examples_text = sheet_to_json("inquiries")
    communication_types = sheet_to_json("communications")
    formatted_examples, formatted_communication = format_examples_and_communication(
        examples_text, communication_types
    )

    # Define system message
    sys_msg = SystemMessage(
        content=(
            "את צ'אטבוט בשם 'מיכל', שנוצר כדי לסייע למשתמשים המבקשים ליצור קשר עם 'פורום מיכל סלה', ארגון הפועל למניעת אלימות נגד נשים ולקידום בטיחותן."
            "תפקידך הוא לתמוך, לכוון ולספק מידע באופן אנושי, דיסקרטי וידידותי. את מדברת בלשון נקבה."
            "קהל היעד שלך:"
            "'שורדות אלימות': נשים שחוו או חוות אלימות."
            "'סביבתן הקרובה': משפחה, חברים, שכנים או קולגות המעוניינים לעזור."
            "'אנשי מקצוע': מטפלים פרטיים או אנשי סיוע העובדים עם נפגעות."
            "המטרות שלך:"
            "'גישה אנושית וידידותית': יצירת תחושת אמון וביטחון אצל המשתמשות והמשתמשים."
            "'מענה מהיר ואפקטיבי': כווני את הפונים לתשובות מועילות, מבוססות תסריטים מוגדרים מראש, תוך התאמה לסיפור האישי."
            "'דיסקרטיות והכלה': וודאי שהשיח תומך, מבין ומכבד."
            "'שימוש בשפה עברית': דברי בעברית פשוטה, נגישה ומכילה."
            "'שקיפות לגבי יכולותיך': אם את לא יודעת את התשובה, הבהירי זאת. אל תספקי מידע חיצוני שלא נמסר בפרומפט."
            "'מקרים דחופים': במידה ומדווח על מקרה אלימות שמתרחש ברגע זה, הסבירי שאת צ'אטבוט ולא אדם, והמליצי לפנות מיד לרשויות או למוקד חירום."
            "בתחילת השיחה תציגי את עצמך בקצרה."
            "תעני תשובות קצרות ותשאלי שאלות המשך שמכווינות את הצורך של המשתמש."
            "כאן יש מידע על סוגי הפניות האפשריות. עבור השאלה של המשתמש, תסווגי לפי סוג הפניה ואז תעני בהתאם למידע שכתוב בהמשך."
        )
    )

    sys_msg.content += f"\n\nדוגמאות לסוגי פניות:\n{formatted_examples}\n\nדוגמאות לסוגי מוקדים:\n{formatted_communication}"

    print(get_display(sys_msg.content))

    # Initialize the Azure LLM
    llm = AzureChatOpenAI(
        api_version=env_vars["api_version"],
        azure_deployment=env_vars["deployment_name"],
    )

    # Define the chatbot prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", sys_msg.content),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt | llm

    # Create chatbot with session-based history
    CHAIN = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="user_input",
        history_messages_key="history",
    )

    print("✅ Chatbot setup completed!")
    
# Function to handle per-user session history
def get_history(session_id):
        if session_id not in STORAGE:
            STORAGE[session_id] = InMemoryHistory()
        return STORAGE[session_id]

def get_chatbot():
    """Returns the cached chatbot instance after ensuring setup is complete."""
    if CHAIN is None:
        raise RuntimeError("❌ Chatbot not initialized. Call setup_chatbot() first.")
    return CHAIN

async def chat(session_id, user_input):
    """Handles a chat request using the session-specific chatbot."""
    
    if user_input == "end session":
        finish_session(CONTAINER, session_id, get_history(session_id))
        return "מקווה שעזרתי, מוזמנ/ת לפנות אלינו בשעות הפעילות ולקבל מענה אנושי"

    chatbot = get_chatbot()
    response = await chatbot.ainvoke(
        {"user_input": user_input},
        config={"configurable": {"session_id": session_id}, "temperature": 0.5, "top_p": 0.7},
    )
    #safe_response = escape_special_chars(response.content)
    return response.content

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """Class to store chat history for each session."""
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


if __name__ == "__main__":
    setup_chatbot()
    async def main():
        while True:
            user_input = input(">>> ")
            chatbot_response = await chat("1", user_input)
            print(get_display(chatbot_response))
    
    asyncio.run(main())
