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
    SESSION_CLEANUP_INTERVAL_MINUTES = int(os.environ.get("SESSION_CLEANUP_INTERVAL_MINUTES", "5"))
    SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "10"))

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

