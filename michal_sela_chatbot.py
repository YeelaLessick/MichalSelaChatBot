# import json
# import os
# from typing import List
# import pandas as pd
# from azure.storage.blob import BlobServiceClient
# from bidi.algorithm import get_display
# from dotenv import load_dotenv
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.messages import BaseMessage, SystemMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_openai import AzureChatOpenAI


# def get_data_from_blob():
#     # Connection string for your Azure Storage Account
#     connection_string = "DefaultEndpointsProtocol=https;AccountName=mihcalselautils;AccountKey=ddiW0Wvm3Cx6AZKFOWTVPuJ97r/xet2kkQupEQOhFKzIpe5iDUv0QBgASgOXGNyLoPSeWNesXYF6+ASt/mWGaw==;EndpointSuffix=core.windows.net"

#     # Initialize BlobServiceClient
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)

#     # Specify the container and file details
#     container_name = "data"
#     blob_name = "michal_sela_table.pdf"
#     download_path = "./downloaded_file.pdf"

#     # Upload the file to the blob container
#     blob_client = blob_service_client.get_blob_client(
#         container=container_name, blob=blob_name
#     )
#     with open(download_path, "wb") as pdf_file:
#         blob_data = blob_client.download_blob().readall()
#         pdf_file.write(blob_data)

#     print(f"Downloaded {blob_name} to {download_path}.")

#     loader = PyPDFLoader(download_path)
#     documents = loader.load()
#     examples_text = " ".join([doc.page_content for doc in documents])
#     return examples_text


# def excel_to_json(sheet):
#     df = pd.read_excel("./modules/michalseladata.xlsx", sheet_name=sheet)
#     json_data = df.to_json(orient="records", indent=4, force_ascii=False)
#     return json_data


# load_dotenv()

# key = os.getenv("AZURE_OPENAI_API_KEY")
# endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# deployment_name = os.getenv("DEPLOYMENT_NAME")
# api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# examples_text = excel_to_json("סוגי פניות")
# communication_types = excel_to_json("מוקדים")
# # Parse the JSON arrays
# examples = json.loads(examples_text)  # Converts JSON string to Python list
# communication = json.loads(communication_types)  # Converts JSON string to Python list

# # Format examples and communication types into readable text
# formatted_examples = "\n".join(
#     f"סוג הפניה: {example['סוג הפניה']}, נקודות חשובות: {example.get('נקודות חשובות', '')}, לאן ניתן להפנות: {example.get('לאן ניתן להפנות', '')}"
#     for example in examples
# )
# formatted_communication = "\n".join(
#     f"סוג מוקד: {comm['סוג מוקד']}, הסבר: {comm.get('הסבר', '')}, מספר: {comm.get('מספר', '')}"
#     for comm in communication
# )


# sys_msg = SystemMessage(
#     content=(
#         "את צ'אטבוט בשם 'מיכל', שנוצר כדי לסייע למשתמשים המבקשים ליצור קשר עם 'פורום מיכל סלע', ארגון הפועל למניעת אלימות נגד נשים ולקידום בטיחותן."
#         "תפקידך הוא לתמוך, לכוון ולספק מידע באופן אנושי, דיסקרטי וידידותי."
#         "קהל היעד שלך:"
#         "'שורדות אלימות': נשים שחוו או חוות אלימות."
#         "'סביבתן הקרובה': משפחה, חברים, שכנים או קולגות המעוניינים לעזור."
#         "'אנשי מקצוע': מטפלים פרטיים או אנשי סיוע העובדים עם נפגעות."
#         "המטרות שלך:"
#         "'גישה אנושית וידידותית': יצירת תחושת אמון וביטחון אצל המשתמשות והמשתמשים."
#         "'מענה מהיר ואפקטיבי': כווני את הפונים לתשובות מועילות, מבוססות תסריטים מוגדרים מראש, תוך התאמה לסיפור האישי."
#         "'דיסקרטיות והכלה': וודאי שהשיח תומך, מבין ומכבד."
#         "'שימוש בשפה עברית': דברי בעברית פשוטה, נגישה ומכילה."
#         "'שקיפות לגבי יכולותיך': אם את לא יודעת את התשובה, הבהירי זאת. אל תספקי מידע חיצוני שלא נמסר בפרומפט."
#         "'מקרים דחופים': במידה ומדווח על מקרה אלימות שמתרחש ברגע זה, הסבירי שאת צ'אטבוט ולא אדם, והמליצי לפנות מיד לרשויות או למוקד חירום."
#         "בתחילת השיחה תציגי את עצמך בקצרה."
#         "תעני תשובות קצרות ותשאלי שאלות המשך שמכווינות את הצורך של המשתמש."
#         "כאן יש מידע על סוגי הפניות האפשריות. עבור השאלה של המשתמש, תסווגי לפי סוג הפניה ואז תעני בהתאם למידע שכתוב בהמשך."
#     )
# )

# # הוספת הטקסט של הדוגמאות לפרומפט
# sys_msg.content += (
#     "\n\nהנה מספר דוגמאות של שיחות, שיוכלו לעזור לך להבין את אופי השאלות והתשובות:"
# )
# sys_msg.content += "\n\nדוגמאות לסוגי פניות:"
# sys_msg.content += f"\n{formatted_examples}"
# sys_msg.content += "\n\nדוגמאות לסוגי מוקדים:"
# sys_msg.content += f"\n{formatted_communication}"

# print(get_display(sys_msg.content))

# llm = AzureChatOpenAI(
#     api_version=api_version,  # type: ignore
#     azure_deployment=deployment_name,
# )


# class InMemoryHistory(BaseChatMessageHistory, BaseModel):
#     messages: List[BaseMessage] = Field(default_factory=list)

#     def add_messages(self, messages: List[BaseMessage]) -> None:
#         self.messages.extend(messages)

#     def clear(self) -> None:
#         self.messages = []


# msg_history = InMemoryHistory()

# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", sys_msg.content),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{user_input}"),
#     ]
# )

# chain = prompt | llm

# chain_with_history = RunnableWithMessageHistory(
#     chain,  # type: ignore (this works, but some typing issue may surface an error, ignore)
#     lambda x: msg_history,
#     input_messages_key="user_input",
#     history_messages_key="history",
# )

# while True:
#     user_input = input(">>> ")
#     response = chain_with_history.invoke(
#         {"user_input": user_input},
#         config={"configurable": {"session_id": "foo"}},
#     )
#     print(get_display(response.content))


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


def load_env_variables():
    load_dotenv()
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
        f"סוג מוקד: {comm['סוג מוקד']}, הסבר: {comm.get('הסבר', '')}, מספר: {comm.get('מספר', '')}"
        for comm in communication
    )

    return formatted_examples, formatted_communication


def initialize_chatbot():
    env_vars = load_env_variables()

    examples_text = excel_to_json("סוגי פניות")
    communication_types = excel_to_json("מוקדים")
    formatted_examples, formatted_communication = format_examples_and_communication(
        examples_text, communication_types
    )

    sys_msg = SystemMessage(
        content=(
            "את צ'אטבוט בשם 'מיכל', שנוצר כדי לסייע למשתמשים המבקשים ליצור קשר עם 'פורום מיכל סלע', ארגון הפועל למניעת אלימות נגד נשים ולקידום בטיחותן."
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

    llm = AzureChatOpenAI(
        api_version=env_vars["api_version"],
        azure_deployment=env_vars["deployment_name"],
    )

    msg_history = InMemoryHistory()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", sys_msg.content),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt | llm
    chain_with_history = RunnableWithMessageHistory(
        chain,  # type: ignore (this works, but some typing issue may surface an error, ignore)
        lambda x: msg_history,
        input_messages_key="user_input",
        history_messages_key="history",
    )

    return chain_with_history


def chat(chain_with_history, user_input):
    response = chain_with_history.invoke(
        {"user_input": user_input},
        config={"configurable": {"session_id": "foo"}},
    )
    return response.content


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


if __name__ == "__main__":
    chain_with_history = initialize_chatbot()
    while True:
        user_input = input(">>> ")
        chatbot_response = chat(chain_with_history, user_input)
        print(get_display(chatbot_response))
