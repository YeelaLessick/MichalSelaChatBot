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
    # For testing: cleanup job runs every 2 minutes, sessions expire after 5 minutes of inactivity
    # For production: set SESSION_CLEANUP_INTERVAL_MINUTES=30 and SESSION_TIMEOUT_MINUTES=60 in environment
    SESSION_CLEANUP_INTERVAL_MINUTES = int(os.environ.get("SESSION_CLEANUP_INTERVAL_MINUTES", "2"))
    SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "5"))
