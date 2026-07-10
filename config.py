#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

""" Bot Configuration """

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    
    # These are the exact attribute names expected by ConfigurationBotFrameworkAuthentication
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "UserAssignedMSI")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")
    
    # Session cleanup configuration
    # A session ends automatically after SESSION_TIMEOUT_MINUTES of inactivity
    # (no new messages), which triggers extraction just like ending with "end".
    # The cleanup job checks every SESSION_CLEANUP_INTERVAL_MINUTES.
    SESSION_CLEANUP_INTERVAL_MINUTES = int(os.environ.get("SESSION_CLEANUP_INTERVAL_MINUTES", "5"))
    SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "30"))


class PostgresConfig:
    """Postgres connection settings.

    Static, non-secret defaults live here so deployments only need to set
    a small number of environment variables (HOST, USER, AZURE_CLIENT_ID).
    Any of these can still be overridden via an env var of the same name.
    """

    # Constants (override via env var of the same name if ever needed)
    PORT = os.environ.get("POSTGRES_PORT", "5432")
    DATABASE = os.environ.get("POSTGRES_DB", "chatbot")
    SSLMODE = os.environ.get("POSTGRES_SSLMODE", "require")

    # AAD on by default; flip to "false" locally to use POSTGRES_PASSWORD.
    USE_AAD = os.environ.get("POSTGRES_USE_AAD", "true").lower() in ("1", "true", "yes")

    # AAD scope for Postgres flexible server
    AAD_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"

    # Deployment-specific (must be set per-environment)
    HOST = os.environ.get("POSTGRES_HOST")
    USER = os.environ.get("POSTGRES_USER")
    # Used by DefaultAzureCredential when multiple MIs are attached
    AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
    # Only used when USE_AAD is false (local dev)
    PASSWORD = os.environ.get("POSTGRES_PASSWORD")


class EmailSummaryConfig:
    """Weekly email summary configuration."""

    RECIPIENT = os.environ.get("WEEKLY_SUMMARY_RECIPIENT", "zoe5559@gmail.com") #"info@michalsela.org.il")
    TIMEZONE = os.environ.get("WEEKLY_SUMMARY_TIMEZONE", "Asia/Jerusalem")
    # Day of week to send on. Monday=0 ... Sunday=6. Default: Sunday.
    SEND_WEEKDAY = int(os.environ.get("WEEKLY_SUMMARY_SEND_WEEKDAY", "6"))
    SEND_HOUR = int(os.environ.get("WEEKLY_SUMMARY_SEND_HOUR", "9"))
    # Debug mode: send the summary every 4 hours instead of weekly (for testing).
    DEBUG_MODE = os.environ.get("SUMMARY_DEBUG_MODE", "false").lower() in ("1", "true", "yes")

    # Azure Communication Services Email
    CONNECTION_STRING = os.environ.get("COMMUNICATION_SERVICES_CONNECTION_STRING", "")
    # Verified ACS mail domain, e.g. "abcd1234.azurecomm.net"
    MAIL_DOMAIN_NAME = os.environ.get("MAIL_DOMAIN_NAME", "")
    # Sender is DoNotReply@<domain>
    SENDER_ADDRESS = f"DoNotReply@{MAIL_DOMAIN_NAME}" if MAIL_DOMAIN_NAME else ""


# רשימת שדות למיצוי מידע משיחות (בעברית)
# List of fields for extracting information from conversations (in Hebrew)
EXTRACTION_FIELDS = [
    "זמן השיחה",
    "נושא הפניה",
    "גיל הפונה",
    "מין הפונה",
    "קרבה לגורם המאיים או לשורדת האלימות",
    "לאן הפנינו",
    "האם פנתה לאן שהפנינו",
    "האם קיבלה מענה טוב",
    "האם היא רוצה שנציג אנושי יחזור אליה",
    "איך הסתיימה השיחה",
]

# ---------- Predefined categories for extraction (used to constrain LLM output) ----------

INQUIRY_SUBJECT_OPTIONS = [
    "נפגעת שמספרת שחווה אלימות",
    "סביבה קרובה שרוצה לעזור לנפגעת",
    "שכנים שרוצים לדווח על אלימות",
    "שאלה על נשקים",
    "אלימות כלכלית",
    "בקשה לסיוע כלכלי",
    "בקשה לסיוע משפטי",
    "פרויקטים להגנה",
    "סיוע סייבר",
    "מרכז לנפגעות תקיפה מינית",
    "פנייה בנוגע להרצאה",
    "סיוע לגברים",
    "סיוע לתושבות חוץ",
    "הפצת תמונות אינטימיות / מענה מתחת לגיל 18",
    "התנדבות",
    "נרקסיזם",
    "קבוצות תמיכה",
    "הדרכה על פרידה",
    "תמרורי אזהרה בזוגיות",
    "תרומה",
    "אלימות כלפי ילדים",
    "בריאות הנפש / התאבדות",
    "פניות לשיתוף פעולה",
    "אחר",
]

CALLER_GENDER_OPTIONS = [
    "נקבה",
    "זכר",
    "אחר",
    "לא ידוע",
]

CALLER_AGE_RANGE_OPTIONS = [
    "מתחת ל-18",
    "18-25",
    "26-35",
    "36-45",
    "46-55",
    "56-65",
    "מעל 65",
    "לא ידוע",
]

RELATIONSHIP_OPTIONS = [
    "שורדת אלימות (הפונה עצמה)",
    "בן/בת זוג",
    "הורה",
    "ילד/ילדה",
    "אח/אחות",
    "קרוב/ת משפחה אחר/ת",
    "חבר/ה",
    "שכן/ה",
    "עמית/ה לעבודה",
    "איש/אשת מקצוע",
    "אחר",
    "לא ידוע",
]

REFERRED_TO_OPTIONS = [
    "משטרה (מוקד 100)",
    "רשות מקומית (מוקד 106)",
    "מוקד משרד הרווחה",
    "השירות הבינלאומי של משרד הרווחה",
    "מוקד סיוע חו\"ל של משרד הרווחה",
    "קו סיוע שקט בהודעות של משרד הרווחה",
    "מוקד משרד הרווחה אלימות במשפחה",
    "עמותת ל.א לא לאלימות נגד נשים",
    "נעמת",
    "עמותת ויצו",
    "בת מלך",
    "מרכזי אלומה",
    "רוח נשית",
    "קווים אדומים",
    "משרד המשפטים",
    "יד לאשה למסורבות גט ועגונות",
    "מבוי סתום",
    "לשכת עורכי הדין שכר מצווה",
    "מערך הסייבר הלאומי",
    "איגוד האינטרנט הישראלי",
    "מרכזי סיוע לנפגעי/ות אלימות מינית",
    "צ׳אט סיוע לנפגעי/ות תקיפה מינית",
    "ארגון עוגן",
    "משרד החוץ",
    "ער\"ן",
    "נט\"ל",
    "סה\"ר",
    "פורום מיכל סלה",
    "לא הופנתה",
]

YES_NO_OPTIONS = ["כן", "לא", "לא ידוע"]

# Fields that accept multiple values (stored as arrays)
MULTI_VALUE_FIELDS = {"inquiry_subject", "referred_to"}

URGENCY_LEVEL_OPTIONS = [
    "חירום - סכנת חיים מיידית",
    "גבוהה - מצב מסוכן",
    "בינונית - דורש טיפול",
    "נמוכה - בקשת מידע בלבד",
]

CONVERSATION_ENDING_OPTIONS = [
    "נטישה",
    "נציגה תחזור",
    "שיחה הושלמה",
]

