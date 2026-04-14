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
    SESSION_CLEANUP_INTERVAL_MINUTES = int(os.environ.get("SESSION_CLEANUP_INTERVAL_MINUTES", "30"))
    SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "60"))

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

URGENCY_LEVEL_OPTIONS = [
    "חירום - סכנת חיים מיידית",
    "גבוהה - מצב מסוכן",
    "בינונית - דורש טיפול",
    "נמוכה - בקשת מידע בלבד",
]

