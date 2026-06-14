"""
One-time migration: Cosmos DB -> Postgres.

Copies all documents from the legacy Cosmos containers into the new
Postgres tables. Idempotent: re-running upserts the same rows.

Required env vars
-----------------
Cosmos source (legacy):
    COSMOSDB_CONNECTIONS_STRING
    COSMOSDB_CONV_DATABASE
    COSMOSDB_CONV_CONTAINER
    COSMOSDB_EXT_DATABASE
    COSMOSDB_EXT_CONTAINER

Postgres target (new):
    POSTGRES_HOST
    POSTGRES_PORT          (default 5432)
    POSTGRES_DB            (default chatbot)
    POSTGRES_USER
    POSTGRES_PASSWORD      OR  POSTGRES_USE_AAD=true
    POSTGRES_SSLMODE       (default require)
    AZURE_CLIENT_ID        (optional, picks a user-assigned MI under AAD mode)

Run
---
    python scripts/migrate_cosmos_to_postgres.py
    python scripts/migrate_cosmos_to_postgres.py --dry-run   # count only

Safe to re-run -- uses ON CONFLICT upsert.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

# Make sibling modules importable when run as `python scripts/migrate_...py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from azure.cosmos import CosmosClient  # noqa: E402

import db  # noqa: E402  (sets up Postgres connection via env)
from psycopg.types.json import Json  # noqa: E402


def _cosmos_container(db_name_env: str, container_env: str):
    conn = os.environ["COSMOSDB_CONNECTIONS_STRING"]
    client = CosmosClient.from_connection_string(conn)
    database = client.get_database_client(os.environ[db_name_env])
    return database.get_container_client(os.environ[container_env])


def migrate_conversations(dry_run: bool = False) -> int:
    print("📥 Reading conversations from Cosmos DB ...")
    src = _cosmos_container("COSMOSDB_CONV_DATABASE", "COSMOSDB_CONV_CONTAINER")
    items = list(src.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
    print(f"   found {len(items)} conversation documents")

    if dry_run:
        return len(items)

    written = 0
    with db._connect() as conn:
        with conn.cursor() as cur:
            for item in items:
                session_id = item.get("SessionId") or item.get("id")
                conversation = item.get("Conversation") or []
                if not session_id:
                    continue
                cur.execute(
                    """
                    INSERT INTO conversations (session_id, conversation, updated_at)
                    VALUES (%s, %s, now())
                    ON CONFLICT (session_id) DO UPDATE
                        SET conversation = EXCLUDED.conversation,
                            updated_at   = now()
                    """,
                    (session_id, Json(conversation)),
                )
                written += 1
                if written % 100 == 0:
                    conn.commit()
                    print(f"   ... {written} conversations written")
        conn.commit()
    print(f"✅ Wrote {written} conversations to Postgres")
    return written


def migrate_extractions(dry_run: bool = False) -> int:
    print("📥 Reading extractions from Cosmos DB ...")
    src = _cosmos_container("COSMOSDB_EXT_DATABASE", "COSMOSDB_EXT_CONTAINER")
    items = list(src.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
    print(f"   found {len(items)} extraction documents")

    if dry_run:
        return len(items)

    written = 0
    with db._connect() as conn:
        with conn.cursor() as cur:
            for item in items:
                # Original session_id was stored on the document; the doc id
                # was usually "{session_id}_extraction".
                session_id = (
                    item.get("SessionId")
                    or (item.get("Metadata") or {}).get("original_session_id")
                    or item.get("id", "").removesuffix("_extraction")
                )
                if not session_id:
                    continue
                extraction = item.get("Extraction") or {}
                metadata = item.get("Metadata") or {}
                cur.execute(
                    """
                    INSERT INTO extractions (session_id, extraction, metadata, created_at)
                    VALUES (%s, %s, %s, now())
                    ON CONFLICT (session_id) DO UPDATE
                        SET extraction = EXCLUDED.extraction,
                            metadata   = EXCLUDED.metadata
                    """,
                    (session_id, Json(extraction), Json(metadata)),
                )
                written += 1
                if written % 100 == 0:
                    conn.commit()
                    print(f"   ... {written} extractions written")
        conn.commit()
    print(f"✅ Wrote {written} extractions to Postgres")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate Cosmos DB -> Postgres")
    parser.add_argument("--dry-run", action="store_true", help="Count source rows; do not write")
    parser.add_argument("--skip-conversations", action="store_true")
    parser.add_argument("--skip-extractions", action="store_true")
    args = parser.parse_args()

    start = time.time()

    if not args.dry_run:
        print("🔧 Ensuring Postgres schema ...")
        db.ensure_schema()

    if not args.skip_conversations:
        migrate_conversations(dry_run=args.dry_run)
    if not args.skip_extractions:
        migrate_extractions(dry_run=args.dry_run)

    elapsed = time.time() - start
    print(f"🎉 Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
