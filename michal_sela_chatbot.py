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

# Global storage for chatbot instance
session_storage = {}
chatbot_chain = None  # Will be initialized once

def setup_chatbot():
    """Initializes chatbot components once at startup."""
    global chatbot_chain

    # Load environment variables
    load_dotenv(override=True)
    env_vars = {
        "key": os.getenv("AZURE_OPENAI_API_KEY"),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_name": os.getenv("DEPLOYMENT_NAME"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
    }

    # Load data for examples and communication centers
    examples_text = excel_to_json("סוגי פניות")
    communication_types = excel_to_json("מוקדים")
    formatted_examples, formatted_communication = format_examples_and_communication(
        examples_text, communication_types
    )

    # Define system message
    sys_msg = SystemMessage(
        content=(
            "את צ'אטבוט בשם 'מיכל', שנוצר כדי לסייע למשתמשים המבקשים ליצור קשר עם 'פורום מיכל סלה', ארגון הפועל למניעת אלימות נגד נשים ולקידום בטיחותן."
            "תפקידך הוא לתמוך, לכוון ולספק מידע באופן אנושי, דיסקרטי וידידותי."
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

    # Function to handle per-user session history
    def get_history(session_id):
        if session_id not in session_storage:
            session_storage[session_id] = InMemoryHistory()
        return session_storage[session_id]

    # Create chatbot with session-based history
    chatbot_chain = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="user_input",
        history_messages_key="history",
    )

    print("✅ Chatbot setup completed!")

def get_chatbot():
    """Returns the cached chatbot instance after ensuring setup is complete."""
    if chatbot_chain is None:
        raise RuntimeError("❌ Chatbot not initialized. Call setup_chatbot() first.")
    return chatbot_chain

def load_env_variables():
    load_dotenv(override=True)
    return {
        "key": os.getenv("AZURE_OPENAI_API_KEY"),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_name": os.getenv("DEPLOYMENT_NAME"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
    }


def get_data_from_blob():
    connection_string = "DefaultEndpointsProtocol=https;AccountName=mihcalselautils;AccountKey=ddiW0Wvm3Cx6AZKFOWTVPuJ97r/xet2kkQupEQOhFKzIpe5iDUv0QBgASgOXGNyLoPSeWNesXYF6+ASt/mWGaw==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = "data"
    blob_name = "michal_sela_table.pdf"
    download_path = "./downloaded_file.pdf"

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    with open(download_path, "wb") as pdf_file:
        pdf_file.write(blob_client.download_blob().readall())

    loader = PyPDFLoader(download_path)
    documents = loader.load()
    return " ".join([doc.page_content for doc in documents])


def excel_to_json(sheet):
    df = pd.read_excel("./michalseladata.xlsx", sheet_name=sheet)
    return df.to_json(orient="records", indent=4, force_ascii=False)


def format_examples_and_communication(examples_text, communication_text):
    examples = json.loads(examples_text)
    communication = json.loads(communication_text)

    formatted_examples = "\n".join(
        f"סוג הפניה: {example['סוג הפניה']}, נקודות חשובות: {example.get('נקודות חשובות', '')}, לאן ניתן להפנות: {example.get('לאן ניתן להפנות', '')}"
        for example in examples
    )

    formatted_communication = "\n".join(
        f"סוג מוקד: {comm['סוג מוקד']}, הסבר: {comm.get('הסבר', '')}, תקשורת: {comm.get('תקשורת', '')}"
        for comm in communication
    )

    return formatted_examples, formatted_communication

def escape_special_chars(text):
    """
    Escapes Telegram's MarkdownV2 reserved characters.
    """
    if not text:
        return text

    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join("\\" + c if c in escape_chars else c for c in text)

def chat(session_id, user_input):
    """Handles a chat request using the session-specific chatbot."""
    chatbot = get_chatbot()
    response = chatbot.invoke(
        {"user_input": user_input},
        config={"configurable": {"session_id": session_id}, "max_tokens": 150, "temperature": 0.4, "top_p": 0.7},
    )
    # Escape special characters before returning the response
    safe_response = escape_special_chars(response.content)
    return safe_response

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """Class to store chat history for each session."""
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


if __name__ == "__main__":
    setup_chatbot()
    while True:
        user_input = input(">>> ")
        chatbot_response = chat("1", user_input)
        print(get_display(chatbot_response))
