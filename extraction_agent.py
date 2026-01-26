import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from config import EXTRACTION_FIELDS

# Load environment variables
load_dotenv()

# Mapping of Hebrew field names to English keys for Cosmos DB
FIELD_NAME_MAPPING = {
    "זמן השיחה": "conversation_time",
    "נושא הפניה": "inquiry_subject",
    "גיל הפונה": "caller_age",
    "מין הפונה": "caller_gender",
    "קרבה לגורם המאיים או לשורדת האלימות": "relationship_to_threat",
    "לאן הפנינו": "referred_to",
    "האם פנתה לאן שהפנינו": "contacted_referral",
    "האם קיבלה מענה טוב": "received_good_response",
    "האם היא רוצה שנציג אנושי יחזור אליה": "wants_human_callback",
}


async def extract_conversation_insights(session_id: str, messages: List[BaseMessage]) -> Dict[str, Any]:
    """
    Extract structured insights from conversation using Azure OpenAI.
    
    Args:
        session_id: Unique session identifier
        messages: List of conversation messages (BaseMessage objects)
    
    Returns:
        Dict containing session_id, timestamp, and extracted data
    """
    try:
        # Convert messages to readable text format
        conversation_text = "\n".join([
            f"{msg.type}: {msg.content}" 
            for msg in messages 
            if hasattr(msg, 'content') and msg.content
        ])
        
        # If no extraction fields configured, return basic metadata only
        if not EXTRACTION_FIELDS or len(EXTRACTION_FIELDS) == 0:
            print(f"⚠️  No extraction fields configured, returning basic metadata only")
            return {
                "session_id": session_id,
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "message_count": len(messages),
                "extraction_note": "No fields configured for extraction"
            }
        
        # Build dynamic extraction prompt based on configured fields
        fields_list = "\n".join([f"- {field}" for field in EXTRACTION_FIELDS])
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""את סוכן חילוץ מידע ממומחה. תפקידך לנתח שיחות עם אנשים שפונים בנושא אלימות במשפחה.
חלצי מידע מובנה מהשיחה הבאה על בסיס השדות הבאים:

{fields_list}

החזירי את התשובה בפורמט JSON בלבד, עם מפתח לכל שדה מהרשימה לעיל.
אם שדה מסוים לא רלוונטי או לא נמצא בשיחה, השתמשי בערך null.
דוגמה לפורמט:
{{
    "שדה1": "ערך",
    "שדה2": null,
    "שדה3": "ערך אחר"
}}
"""),
            ("human", "שיחה:\n{conversation}")
        ])
        
        # Initialize Azure OpenAI
        llm = AzureChatOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("DEPLOYMENT_NAME"),
            temperature=0.1  # Lower temperature for more consistent extraction
        )
        
        chain = extraction_prompt | llm
        
        # Execute extraction
        result = await chain.ainvoke({"conversation": conversation_text})
        
        # Parse the JSON response from the LLM
        extracted_data = {}
        if hasattr(result, 'content') and result.content:
            try:
                # Try to parse as JSON
                hebrew_data = json.loads(result.content)
                
                # Map Hebrew keys to English keys for Cosmos DB
                extracted_data = {}
                for hebrew_key, value in hebrew_data.items():
                    english_key = FIELD_NAME_MAPPING.get(hebrew_key, hebrew_key)
                    extracted_data[english_key] = value
                    
            except json.JSONDecodeError:
                # If not valid JSON, store as raw text
                print(f"⚠️  LLM response was not valid JSON, storing as raw text")
                extracted_data = {"raw_response": result.content}
        
        return {
            "session_id": session_id,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "message_count": len(messages),
            "extracted_fields": extracted_data
        }
        
    except Exception as e:
        print(f"❌ Extraction failed for session {session_id}: {str(e)}")
        return {
            "session_id": session_id,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "message_count": len(messages) if messages else 0,
            "extraction_error": str(e)
        }


async def extract_with_retry(session_id: str, messages: List[BaseMessage], max_retries: int = 3) -> Dict[str, Any]:
    """
    Extract conversation insights with retry logic.
    
    Args:
        session_id: Unique session identifier
        messages: List of conversation messages
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Dict containing extraction results or error information
    """
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            print(f"🔄 Extraction attempt {attempt + 1}/{max_retries} for session {session_id}")
            
            result = await extract_conversation_insights(session_id, messages)
            
            # Check if extraction was successful (no error field)
            if "extraction_error" not in result:
                print(f"✅ Extraction successful for session {session_id} on attempt {attempt + 1}")
                return result
            else:
                last_error = result.get("extraction_error")
                print(f"⚠️ Extraction returned error on attempt {attempt + 1}: {last_error}")
                
        except Exception as e:
            last_error = str(e)
            print(f"❌ Extraction attempt {attempt + 1} failed for session {session_id}: {last_error}")
        
        attempt += 1
        
        # Exponential backoff: wait 2^attempt seconds before retry
        if attempt < max_retries:
            wait_time = 2 ** attempt
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            await asyncio.sleep(wait_time)
    
    # All retries exhausted
    print(f"❌ All {max_retries} extraction attempts failed for session {session_id}")
    return {
        "session_id": session_id,
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "message_count": len(messages) if messages else 0,
        "extraction_error": f"Failed after {max_retries} attempts. Last error: {last_error}"
    }
