import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from config import (
    EXTRACTION_FIELDS,
    INQUIRY_SUBJECT_OPTIONS,
    CALLER_GENDER_OPTIONS,
    CALLER_AGE_RANGE_OPTIONS,
    RELATIONSHIP_OPTIONS,
    REFERRED_TO_OPTIONS,
    YES_NO_OPTIONS,
    URGENCY_LEVEL_OPTIONS,
    CONVERSATION_ENDING_OPTIONS,
    MULTI_VALUE_FIELDS,
)

# Load environment variables
load_dotenv()

# Mapping of Hebrew field names to English keys for storage
FIELD_NAME_MAPPING = {
    "זמן השיחה": "conversation_time",
    "נושא הפניה": "inquiry_subject",
    "גיל הפונה": "caller_age",
    "מין הפונה": "caller_gender",
    "קרבה לגורם המאיים או לשורדת האלימות": "relationship_to_threat",
    "לאן הפנינו": "referred_to",
    "האם היא רוצה שנציג אנושי יחזור אליה": "wants_human_callback",
    "רמת דחיפות": "urgency_level",
    "איך הסתיימה השיחה": "conversation_ending",
}


def infer_conversation_ending(messages: List[BaseMessage]) -> str:
    """Static fallback classifier over the recent message window."""
    if not messages:
        return "נטישה"

    recent_messages = [
        msg for msg in messages[-8:]
        if str(getattr(msg, "content", "") or "").strip()
    ]
    if not recent_messages:
        return "נטישה"

    def _msg_type(msg: BaseMessage) -> str:
        return str(getattr(msg, "type", "") or "").strip().lower()

    callback_markers = {
        "נציג", "נציגה", "יחזור", "תחזור", "חזרה", "callback", "call back",
        "לחזור אליי", "לחזור אלי", "שיחזרו", "שיחה עם נציג", "שיחה עם נציגה",
    }
    for msg in recent_messages:
        msg_type = _msg_type(msg)
        if msg_type not in {"human", "user"}:
            continue
        content = str(getattr(msg, "content", "") or "").lower()
        if any(marker in content for marker in callback_markers):
            return "נציגה תחזור"

    closing_markers = {
        "תודה", "תודה רבה", "להתראות", "סיום", "נגמר", "סיימנו", "bye", "goodbye", "thanks",
    }

    last_message = recent_messages[-1]
    last_type = _msg_type(last_message)
    last_content = str(getattr(last_message, "content", "") or "").strip().lower()

    if any(marker in last_content for marker in closing_markers):
        return "שיחה הושלמה"

    if last_type in {"assistant", "ai"}:
        # When the assistant spoke last without callback intent, treat as completed.
        return "שיחה הושלמה"

    # User spoke last without clear closure and no callback request -> likely abrupt end.
    return "נטישה"


async def infer_conversation_ending_with_agent(
    messages: List[BaseMessage], llm: Optional[AzureChatOpenAI] = None
) -> Optional[str]:
    """Ask the model to classify conversation ending from the full conversation.

    Returns one of the configured tags, or None when the model is uncertain/invalid.
    """
    if not messages:
        return None

    full_messages = [
        msg for msg in messages
        if str(getattr(msg, "content", "") or "").strip()
    ]
    if not full_messages:
        return None

    conversation_text = "\n".join(
        f"{getattr(msg, 'type', 'unknown')}: {getattr(msg, 'content', '')}"
        for msg in full_messages
    )

    local_llm = llm or AzureChatOpenAI(
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        request_timeout=20,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """את מסווגת את אופן סיום השיחה. החזירי ערך אחד בלבד מתוך:
- נטישה
- שיחה הושלמה
- נציגה תחזור

הגדרות מחייבות:
1) נציגה תחזור:
- אם הפונה ביקשה במפורש שיחזרו אליה נציג/ה אנושי/ת.
- כולל ניסוחים כמו "תחזרו אליי", "שנציג יחזור", "אפשר לדבר עם נציגה".

2) שיחה הושלמה:
- הפונה קיבלה מענה למה שביקשה, ואין שאלה פתוחה שלא נענתה.
- לרוב יש סימן סיום טבעי כמו תודה/להתראות/אישור שהכול ברור.
- אפשר לסווג כהושלמה גם בלי "תודה" אם ברור שהמענה ניתן במלואו ולא נשאר צורך פתוח.

3) נטישה:
- השיחה נעצרה בלי אינדיקציה ברורה שהנושא נסגר.
- במיוחד אם נשארה שאלה פתוחה, בקשה שלא נענתה, או שהעוזרת ביקשה הבהרה והפונה לא המשיכה.
- אם לא ברור אם הפונה קיבלה מענה מלא - העדיפי נטישה.

כללי הכרעה:
- השתמשי בכל ההודעות שסופקו לך (כל השיחה), ותני משקל מיוחד לשלבי הסיום.
- סדר עדיפויות במקרה של סימנים מעורבים: נציגה תחזור > שיחה הושלמה > נטישה.
- אם אין ודאות מספקת לקבוע בביטחון, החזירי decidable=false.

החזירי JSON בלבד בפורמט:
{"decidable": true/false, "conversation_ending": "נטישה|שיחה הושלמה|נציגה תחזור|null"}
""",
        ),
        ("human", "הודעות אחרונות:\n{conversation}"),
    ])

    try:
        result = await asyncio.wait_for(
            (prompt | local_llm).ainvoke({"conversation": conversation_text}),
            timeout=25,
        )
        raw = str(getattr(result, "content", "") or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        parsed = json.loads(raw)
        if not bool(parsed.get("decidable", False)):
            return None

        candidate = str(parsed.get("conversation_ending") or "").strip()
        if candidate in set(CONVERSATION_ENDING_OPTIONS):
            return candidate
        return None
    except Exception:
        return None


async def resolve_conversation_ending(
    value: Any,
    messages: List[BaseMessage],
    llm: Optional[AzureChatOpenAI] = None,
) -> str:
    """Agent-first ending decision with static fallback only when undecidable."""
    allowed = set(CONVERSATION_ENDING_OPTIONS)
    text_value = str(value).strip() if value is not None else ""
    if text_value in allowed:
        return text_value

    agent_decision = await infer_conversation_ending_with_agent(messages, llm=llm)
    if agent_decision in allowed:
        return agent_decision

    return infer_conversation_ending(messages)


def _get_extraction_deployment_name() -> str | None:
    """Prefer a dedicated extraction deployment, then fall back to the chat deployment."""
    return os.getenv("EXTRACTION_DEPLOYMENT_NAME") or os.getenv("DEPLOYMENT_NAME")


def _model_supports_custom_temperature(deployment_name: str | None) -> bool:
    """Whether a deployment accepts a non-default ``temperature``.

    Reasoning models such as the gpt-5 / o-series family only support the
    default temperature of 1 and return a 400 error for any other value.
    """
    if not deployment_name:
        return True
    name = deployment_name.lower()
    unsupported_prefixes = ("gpt-5", "o1", "o3", "o4")
    return not name.startswith(unsupported_prefixes)


async def extract_conversation_insights(session_id: str, messages: List[BaseMessage], session_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    print(f"🔍 Starting extraction for session {session_id} with {len(messages)} messages")
    try:
        # Convert messages to readable text format
        conversation_text = "\n".join([
            f"{msg.type}: {msg.content}" 
            for msg in messages 
            if hasattr(msg, 'content') and msg.content
        ])
        
        # If no extraction fields configured, return basic metadata only
        if not EXTRACTION_FIELDS or len(EXTRACTION_FIELDS) == 0:
            print(f"⚠️ No extraction fields configured, returning basic metadata only")
            return {
                "session_id": session_id,
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "message_count": len(messages),
                "extraction_note": "No fields configured for extraction"
            }
        
        # Build dynamic extraction prompt with constrained categories
        def _fmt(options):
            return " | ".join(options)

        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""את סוכן חילוץ מידע ממומחה. תפקידך לנתח שיחות עם אנשים שפונים בנושא אלימות במשפחה.
חלצי מידע מובנה מהשיחה הבאה. עבור כל שדה, בחרי **רק** מתוך הערכים המותרים שמופיעים בסוגריים.
אם שדה לא רלוונטי או לא נמצא בשיחה, השתמשי בערך null.

שדות לחילוץ:
- "נושא הפניה" (מערך — ניתן לבחור מספר ערכים): [{_fmt(INQUIRY_SUBJECT_OPTIONS)}]
- "גיל הפונה": [{_fmt(CALLER_AGE_RANGE_OPTIONS)}]
- "מין הפונה": [{_fmt(CALLER_GENDER_OPTIONS)}]
- "קרבה לגורם המאיים או לשורדת האלימות": [{_fmt(RELATIONSHIP_OPTIONS)}]
- "לאן הפנינו" (מערך — ניתן לבחור מספר ערכים): [{_fmt(REFERRED_TO_OPTIONS)}]
- "האם היא רוצה שנציג אנושי יחזור אליה": [{_fmt(YES_NO_OPTIONS)}]
- "רמת דחיפות": [{_fmt(URGENCY_LEVEL_OPTIONS)}]
- "איך הסתיימה השיחה": [{_fmt(CONVERSATION_ENDING_OPTIONS)}]

חשוב מאוד:
1. הערכים חייבים להיות **בדיוק** כפי שמופיעים ברשימה. אל תשני ניסוח, אל תוסיפי מילים.
2. שדות מסומנים "מערך" — החזירי רשימה (array) גם אם יש ערך אחד בלבד, לדוגמה: ["ערך1", "ערך2"].
   אם אין ערך, החזירי null.

החזירי JSON בלבד:
{{{{
    "נושא הפניה": ["...", "..."],
    "גיל הפונה": "...",
    "מין הפונה": "...",
    "קרבה לגורם המאיים או לשורדת האלימות": "...",
    "לאן הפנינו": ["...", "..."],
    "האם היא רוצה שנציג אנושי יחזור אליה": "...",
    "רמת דחיפות": "...",
    "איך הסתיימה השיחה": "..."
}}}}
"""),
            ("human", "שיחה:\n{conversation}")
        ])
        
        # Initialize Azure OpenAI with timeout.
        # NOTE: langchain_openai defaults temperature to 0.7 when it is not set,
        # and models like gpt-5 / o-series reject anything other than 1. So we
        # must set temperature EXPLICITLY in both cases (never omit it).
        deployment_name = _get_extraction_deployment_name()
        llm_kwargs = {
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
            "azure_deployment": deployment_name,
            "request_timeout": 60,  # 60 second timeout
        }
        if _model_supports_custom_temperature(deployment_name):
            # Lower temperature for more consistent extraction
            llm_kwargs["temperature"] = 0.1
        else:
            # gpt-5 / o-series only accept the default value of 1
            llm_kwargs["temperature"] = 1
        llm = AzureChatOpenAI(**llm_kwargs)
        
        chain = extraction_prompt | llm
        
        # Execute extraction with timeout
        print(f"📞 Calling Azure OpenAI for extraction...")
        result = await asyncio.wait_for(
            chain.ainvoke({"conversation": conversation_text}),
            timeout=90  # 90 second total timeout
        )
        
        print (f"✅ Extraction completed for session {session_id}")

        # Parse the JSON response from the LLM
        extracted_data = {}
        if hasattr(result, 'content') and result.content:
            try:
                # Try to parse as JSON
                hebrew_data = json.loads(result.content)
                
                # Map Hebrew keys to English keys for storage
                extracted_data = {}
                for hebrew_key, value in hebrew_data.items():
                    english_key = FIELD_NAME_MAPPING.get(hebrew_key, hebrew_key)
                    # Normalise multi-value fields: ensure they are always lists
                    if english_key in MULTI_VALUE_FIELDS:
                        if value is None:
                            extracted_data[english_key] = []
                        elif isinstance(value, str):
                            extracted_data[english_key] = [value]
                        elif isinstance(value, list):
                            extracted_data[english_key] = value
                        else:
                            extracted_data[english_key] = [str(value)]
                    else:
                        extracted_data[english_key] = value
                    
            except json.JSONDecodeError:
                # If not valid JSON, store as raw text
                print(f"⚠️  LLM response was not valid JSON, storing as raw text")
                extracted_data = {"raw_response": result.content}
        
        # Compute conversation duration from session metadata (created_at → last_modified)
        conversation_duration_minutes = None
        if session_metadata:
            created = session_metadata.get("created_at")
            last_mod = session_metadata.get("last_modified")
            if created and last_mod:
                try:
                    delta = last_mod - created
                    conversation_duration_minutes = round(delta.total_seconds() / 60, 1)
                except Exception:
                    pass

        # Guarantee this tag exists in every extraction payload.
        extracted_data["conversation_ending"] = await resolve_conversation_ending(
            extracted_data.get("conversation_ending"), messages, llm=llm
        )
        extracted_data["conversation_time"] = conversation_duration_minutes

        return {
            "session_id": session_id,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "message_count": len(messages),
            "extracted_fields": extracted_data
        }
    
    except asyncio.TimeoutError:
        print(f"⏱️  Extraction timed out for session {session_id}")
        return {
            "session_id": session_id,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "message_count": len(messages) if messages else 0,
            "extracted_fields": {
                "conversation_ending": infer_conversation_ending(messages),
                "conversation_time": None,
            },
            "extraction_error": "Extraction timed out after 90 seconds"
        }
        
    except Exception as e:
        print(f"❌ Extraction failed for session {session_id}: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return {
            "session_id": session_id,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "message_count": len(messages) if messages else 0,
            "extracted_fields": {
                "conversation_ending": infer_conversation_ending(messages),
                "conversation_time": None,
            },
            "extraction_error": str(e)
        }


async def extract_with_retry(session_id: str, messages: List[BaseMessage], max_retries: int = 3, session_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    attempt = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            print(f"🔄 Extraction attempt {attempt + 1}/{max_retries} for session {session_id}")
            
            result = await extract_conversation_insights(session_id, messages, session_metadata=session_metadata)
            
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
