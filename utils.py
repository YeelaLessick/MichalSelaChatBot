# def get_data_from_blob():
#     connection_string = "DefaultEndpointsProtocol=https;AccountName=samichalselaprod01;AccountKey=ThgCKgZT5h61GMq/OPqADv/R7B1oe8ODprIR0MSInTHL/toAUWC6j+fvk38ZzCiEVhgsGESXsKKk+AStOlwjxw==;EndpointSuffix=core.windows.net"
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     container_name = "data"
#     blob_name = "michal_sela_table.pdf"
#     download_path = "./downloaded_file.pdf"

#     blob_client = blob_service_client.get_blob_client(
#         container=container_name, blob=blob_name
#     )
#     with open(download_path, "wb") as pdf_file:
#         pdf_file.write(blob_client.download_blob().readall())

#     loader = PyPDFLoader(download_path)
#     documents = loader.load()
#     return " ".join([doc.page_content for doc in documents])


import json

import pandas as pd


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

# def escape_special_chars(text: str) -> str:
#     """
#     Escapes all characters that are reserved in Telegram MarkdownV2.
#     """
#     if not text:
#         return text

#     escape_chars = r'_*\[\]()~`>#+-=|{}.!'
#     return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)