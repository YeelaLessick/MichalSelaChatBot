"""
Postgres-backed persistence for the Michal Sela chatbot.

Two tables (both in the same database):

    conversations(session_id PK, conversation JSONB, updated_at)
    extractions(session_id PK, extraction JSONB, metadata JSONB,
                channel TEXT GENERATED, created_at)

Schema is created on first connect (idempotent).

Authentication
--------------
Two modes are supported, selected via config / env vars:

* Microsoft Entra ID (recommended in Azure):
    - PostgresConfig.USE_AAD is True (default)
    - PostgresConfig.HOST, USER (= managed-identity name) set via env
    - Token fetched at connect time via `azure.identity.DefaultAzureCredential`
      against PostgresConfig.AAD_SCOPE.
    - AZURE_CLIENT_ID can be set to pick a specific user-assigned identity.

* Password auth (local dev / fallback):
    - POSTGRES_PASSWORD set, POSTGRES_USE_AAD=false.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone

import psycopg
from psycopg.types.json import Json

from config import PostgresConfig

logger = logging.getLogger(__name__)

# Token cache: AAD tokens are valid ~1h, refresh ~5 min before expiry.
_token_cache: dict = {"token": None, "expires_at": 0.0}
_token_lock = threading.Lock()
_schema_initialised = False
_schema_lock = threading.Lock()


def _build_conninfo(password: str | None) -> str:
    """Compose a libpq conninfo string from PostgresConfig + password."""
    if not PostgresConfig.HOST:
        raise RuntimeError("POSTGRES_HOST environment variable is not set.")
    if not PostgresConfig.USER:
        raise RuntimeError("POSTGRES_USER environment variable is not set.")

    parts = [
        f"host={PostgresConfig.HOST}",
        f"port={PostgresConfig.PORT}",
        f"dbname={PostgresConfig.DATABASE}",
        f"user={PostgresConfig.USER}",
        f"sslmode={PostgresConfig.SSLMODE}",
        "connect_timeout=10",
    ]
    if password:
        escaped = password.replace("\\", "\\\\").replace("'", "\\'")
        parts.append(f"password='{escaped}'")
    return " ".join(parts)


def _get_aad_token() -> str:
    """Fetch (and cache) a short-lived Entra token to use as the Postgres password."""
    now = time.time()
    with _token_lock:
        cached = _token_cache["token"]
        if cached and _token_cache["expires_at"] - now > 300:
            return cached

        from azure.identity import ClientSecretCredential, DefaultAzureCredential

        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = PostgresConfig.AZURE_CLIENT_ID or os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")

        # Prefer an explicit service principal when the app is configured for it.
        if tenant_id and client_id and client_secret:
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        else:
            credential = DefaultAzureCredential(
                managed_identity_client_id=client_id or None
            )

        try:
            access = credential.get_token(PostgresConfig.AAD_SCOPE)
            _token_cache["token"] = access.token
            _token_cache["expires_at"] = float(access.expires_on)
            return access.token
        except Exception as exc:
            if PostgresConfig.PASSWORD:
                logger.warning(
                    "AAD token acquisition failed for Postgres; falling back to POSTGRES_PASSWORD: %s",
                    exc,
                )
                return PostgresConfig.PASSWORD
            raise RuntimeError(
                "Postgres AAD authentication failed and POSTGRES_PASSWORD is not set. "
                "Configure AZURE_TENANT_ID/AZURE_CLIENT_ID/AZURE_CLIENT_SECRET for a service principal, "
                "or enable a managed identity for the app and grant it access to Postgres."
            ) from exc


def _get_password() -> str | None:
    """Pick the right password source based on config."""
    if PostgresConfig.USE_AAD:
        return _get_aad_token()
    if not PostgresConfig.PASSWORD:
        raise RuntimeError(
            "POSTGRES_PASSWORD is required when POSTGRES_USE_AAD is not enabled."
        )
    return PostgresConfig.PASSWORD


def _connect() -> psycopg.Connection:
    """Open a fresh Postgres connection."""
    return psycopg.connect(_build_conninfo(_get_password()))


# --- Schema ------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
    session_id   TEXT PRIMARY KEY,
    conversation JSONB NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS extractions (
    session_id   TEXT PRIMARY KEY,
    extraction   JSONB NOT NULL,
    metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    channel      TEXT GENERATED ALWAYS AS (metadata->>'channel') STORED,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_extractions_channel ON extractions (channel);
CREATE INDEX IF NOT EXISTS idx_extractions_created_at ON extractions (created_at);
CREATE INDEX IF NOT EXISTS idx_extractions_fields_gin
    ON extractions USING GIN (extraction);
"""


def ensure_schema() -> None:
    """Create tables/indexes if missing. Safe to call repeatedly."""
    global _schema_initialised
    if _schema_initialised:
        return
    with _schema_lock:
        if _schema_initialised:
            return
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(_SCHEMA_SQL)
            conn.commit()
        _schema_initialised = True
        logger.info("✅ Postgres schema ensured (conversations, extractions)")


def connect_to_db() -> None:
    """Initialise schema. Call once at startup."""
    ensure_schema()


# --- Message serialisation ---------------------------------------------------


def messages_to_json(messages):
    """Convert list of BaseMessage objects to JSON-serializable list."""
    if not messages:
        return []

    serialized = []
    for msg in messages:
        try:
            msg_dict = {
                "type": str(msg.type) if hasattr(msg, "type") else "unknown",
                "content": str(msg.content) if hasattr(msg, "content") else "",
            }
            serialized.append(msg_dict)
        except Exception as e:
            logger.warning("Error serializing message: %s", e)
            serialized.append({"type": "error", "content": str(msg)})

    try:
        json.dumps(serialized)
    except Exception as e:
        logger.error("Serialized messages are not JSON compatible: %s", e)
        return [{"type": "error", "content": "Failed to serialize messages"}]

    return serialized


def _to_json_compatible(value):
    """Recursively convert values to JSON-serializable structures."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc).isoformat()
        return value.isoformat()

    if isinstance(value, Mapping):
        # JSON object keys must be strings.
        return {str(k): _to_json_compatible(v) for k, v in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_to_json_compatible(v) for v in value]

    # Fallback for uncommon types (UUID, Enum, Decimal, custom objects).
    return str(value)


# --- Public write operations -------------------------------------------------


def save_conversation(session_id: str, messages) -> None:
    """Upsert the conversation message history for a session."""
    payload = messages_to_json(messages)
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversations (session_id, conversation, updated_at)
                    VALUES (%s, %s, now())
                    ON CONFLICT (session_id) DO UPDATE
                        SET conversation = EXCLUDED.conversation,
                            updated_at   = now()
                    """,
                    (session_id, Json(payload)),
                )
            conn.commit()
        logger.info("✅ Conversation stored for session %s", session_id)
    except Exception as e:
        logger.error("❌ Error storing conversation for %s: %s", session_id, e)


def save_extraction(session_id: str, extraction_data, session_metadata=None) -> None:
    """Upsert the extracted-fields document for a session."""
    meta = dict(session_metadata or {})
    meta.setdefault("extraction_timestamp", datetime.now(timezone.utc).isoformat())
    meta.setdefault("original_session_id", session_id)
    meta.setdefault("channel", meta.get("channel", "unknown"))
    extraction_payload = _to_json_compatible(extraction_data)
    metadata_payload = _to_json_compatible(meta)

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO extractions (session_id, extraction, metadata, created_at)
                    VALUES (%s, %s, %s, now())
                    ON CONFLICT (session_id) DO UPDATE
                        SET extraction = EXCLUDED.extraction,
                            metadata   = EXCLUDED.metadata
                    """,
                    (session_id, Json(extraction_payload), Json(metadata_payload)),
                )
            conn.commit()
        logger.info("✅ Extraction stored for session %s", session_id)
    except Exception as e:
        logger.error("❌ Error storing extraction for %s: %s", session_id, e)


# --- Misc helpers kept for backwards compatibility ---------------------------


def is_end_conversation_message(last_message: str) -> bool:
    """Return True when the user signalled end-of-conversation."""
    if last_message and last_message.strip().lower() == "end":
        logger.info("End of conversation detected.")
        return True
    return False
