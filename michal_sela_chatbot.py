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
import asyncio
from cosmosdb import is_end_conversation_message, send_convessation_to_cosmos, send_extracted_data, connect_to_cosmos
from extraction_agent import extract_with_retry

# Global storage for chatbot instance
session_storage = {}
chatbot_chain = None  # Will be initialized once
conv_container = None
ext_container = None

def setup_chatbot():
    """Initializes chatbot components once at startup."""
    global chatbot_chain, conv_container, ext_container

    # Load environment variables
    load_dotenv(override=True)
    env_vars = {
        "key": os.getenv("AZURE_OPENAI_API_KEY"),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_name": os.getenv("DEPLOYMENT_NAME"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "connection_string": os.getenv("COSMOSDB_CONNECTIONS_STRING"),
        "conversations_database_name": os.getenv("COSMOSDB_CONV_DATABASE"),
        "conversations_container_name": os.getenv("COSMOSDB_CONV_CONTAINER"),
        "extracted_data_database_name": os.getenv("COSMOSDB_EXT_DATABASE"),
        "extracted_data_container_name": os.getenv("COSMOSDB_EXT_CONTAINER"),
    }

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

    conv_container = connect_to_cosmos(
        env_vars["connection_string"],
        env_vars["conversations_database_name"],
        env_vars["conversations_container_name"],
    )

    ext_container = connect_to_cosmos(
        env_vars["connection_string"],
        env_vars["extracted_data_database_name"],
        env_vars["extracted_data_container_name"],
    )

    # add a test message to the cosmos db to verify connection
    print("Testing Cosmos DB connection by sending a test message...")
    send_convessation_to_cosmos("test_session", [{"type": "system", "content": "Test message to verify Cosmos DB connection."}])

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

def get_data_from_blob():
    connection_string = "DefaultEndpointsProtocol=https;AccountName=samichalselaprod01;AccountKey=ThgCKgZT5h61GMq/OPqADv/R7B1oe8ODprIR0MSInTHL/toAUWC6j+fvk38ZzCiEVhgsGESXsKKk+AStOlwjxw==;EndpointSuffix=core.windows.net"
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

def sheet_to_json(sheet):
    print(f"🔍 Processing sheet: {sheet}")
    sheet_id = "171lvGDgFuFj4TV_Htz1fSkbKyAL30imCI8-UluwqlBA"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet}"
    try:
        # Read the CSV data
        df = pd.read_csv(url, encoding='utf-8')
        
        print(f"📊 Raw data: {len(df)} rows, {len(df.columns)} columns")
        print(f"📝 Original columns: {df.columns.tolist()}")
        
        # Clean column names
        df.columns = df.columns.str.replace('', '', regex=True).str.strip()
        
        # Remove completely empty rows
        df.dropna(how='all', inplace=True)
        
        print("📊 Final cleaned columns:", df.columns.tolist())
        print(f"📊 Number of data rows: {len(df)}")
        
        return df.to_json(orient="records", indent=4, force_ascii=False)
        
    except Exception as e:
        print(f"❌ Error processing sheet {sheet}: {str(e)}")
        return "[]"  # Return empty JSON array on error

def format_examples_and_communication(examples_text, communication_text):
    examples = json.loads(examples_text)
    communication = json.loads(communication_text)

    formatted_examples = "\n".join(
        f"סוג הפניה: {example.get('סוג הפניה', '')}, נקודות חשובות: {example.get('נקודות חשובות', '')}, לאן ניתן להפנות: {example.get('לאן ניתן להפנות', '')}"
        for example in examples
        if 'סוג הפניה' in example
    )

    formatted_communication = "\n".join(
        f"סוג מוקד: {comm.get('סוג מוקד', '')}, הסבר: {comm.get('הסבר', '')}, תקשורת: {comm.get('תקשורת', '')}"
        for comm in communication
        if 'סוג מוקד' in comm
    )

    return formatted_examples, formatted_communication

async def chat(session_id, user_input):
    """Handles a chat request using the session-specific chatbot."""
    chatbot = get_chatbot()

    if user_input is None:
        user_input = ""

    if is_end_conversation_message(user_input):
        history = session_storage.get(session_id)
        print(f"conversation end detected for session {session_id}")
        if history and len(history.messages) > 0:
            # Create background task for extraction and saving
            # Don't await - let it run asynchronously
            print(f"🚀 Started background extraction task for session {session_id}")
            asyncio.create_task(process_conversation_end(conv_container, ext_container, session_id, history.messages))
        
        # Immediately return response to user
        return "השיחה הסתיימה. תודה שפנית אלינו."

    response = await chatbot.ainvoke(
        {"user_input": user_input},
        config={"configurable": {"session_id": session_id}, "temperature": 0.5, "top_p": 0.7},
    )
    
    if response is not None and response.content is not None:
        return response.content
    return ""


async def process_conversation_end(conv_container, ext_container, session_id: str, messages: List[BaseMessage]):
    """
    Background task to extract insights and save conversation to Cosmos DB.
    Runs asynchronously without blocking the user response.
    """
    try:        
        # Save conversation first
        send_convessation_to_cosmos(conv_container, session_id, messages)
        
        # Extract insights with retry logic
        extraction_data = await extract_with_retry(session_id, messages, max_retries=3)
        
        # Save extraction data separately
        send_extracted_data(ext_container, session_id, extraction_data)
        
        # Cleanup session from memory
        if session_id in session_storage:
            del session_storage[session_id]
            print(f"🧹 Cleaned up session {session_id} from memory")
        
        print(f"✅ Background processing complete for session {session_id}")
        
    except Exception as e:
        print(f"❌ Error in background conversation processing for session {session_id}: {str(e)}")
        # Even if extraction fails, try to save the raw conversation
        try:
            send_convessation_to_cosmos(conv_container, session_id, messages)
            print(f"⚠️  Saved conversation without extraction data for session {session_id}")
        except Exception as save_error:
            print(f"❌ Failed to save conversation for session {session_id}: {str(save_error)}")
            print(f"⚠️  Saved conversation without extraction data for session {session_id}")
        except Exception as save_error:
            print(f"❌ Failed to save conversation for session {session_id}: {str(save_error)}")




class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """Class to store chat history for each session."""
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Override to prevent default behavior that would duplicate messages."""
        pass

    def add_user_message(self, message: str) -> None:
        """Add a user message - called by RunnableWithMessageHistory."""
        from langchain_core.messages import HumanMessage
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        """Add an AI message - called by RunnableWithMessageHistory."""
        from langchain_core.messages import AIMessage
        self.messages.append(AIMessage(content=message))

    def get_messages(self) -> List[BaseMessage]:
        return self.messages
    
    def get_messages_as_json(self) -> str:
        """Returns the chat history as a JSON string."""
        serialized = []
        for msg in self.messages:
            serialized.append({
                "type": msg.type,
                "content": msg.content
            })
        return json.dumps(serialized, ensure_ascii=False, indent=4)

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
