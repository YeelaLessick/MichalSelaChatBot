"""Daily email summary service for conversation extractions."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from azure.communication.email import EmailClient

from config import EmailSummaryConfig
from db import _connect

logger = logging.getLogger(__name__)

PRIORITY_ENDING = "נציגה תחזור"
PRIORITY_URGENCIES = {
    "חירום - סכנת חיים מיידית",
    "גבוהה - מצב מסוכן",
}

URGENCY_ORDER = {
    "חירום - סכנת חיים מיידית": 0,
    "גבוהה - מצב מסוכן": 1,
    "בינונית - דורש טיפול": 2,
    "נמוכה - בקשת מידע בלבד": 3,
}


def _urgency_sort_key(value: str | None) -> int:
    if not value:
        return 99
    return URGENCY_ORDER.get(value, 99)


def _extract_fields(extraction: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(extraction, dict):
        return {}
    extracted = extraction.get("extracted_fields")
    if isinstance(extracted, dict):
        return extracted
    return extraction


def _format_list(value: Any) -> str:
    if isinstance(value, list):
        values = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(values) if values else "-"
    if value is None:
        return "-"
    text = str(value).strip()
    return text if text else "-"


def _build_row_html(item: dict[str, Any]) -> str:
    fields = item["fields"]
    created_local = item["created_local"].strftime("%Y-%m-%d %H:%M")
    return (
        "<tr>"
        f"<td>{created_local}</td>"
        f"<td>{item['session_id']}</td>"
        f"<td>{fields.get('conversation_ending', '-')}</td>"
        f"<td>{fields.get('urgency_level', '-')}</td>"
        f"<td>{_format_list(fields.get('inquiry_subject'))}</td>"
        f"<td>{_format_list(fields.get('referred_to'))}</td>"
        f"<td>{fields.get('wants_human_callback', '-')}</td>"
        "</tr>"
    )


def _build_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<p>אין שיחות בקטגוריה זו.</p>"

    rows = "".join(_build_row_html(item) for item in items)
    return (
        "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;width:100%;'>"
        "<thead>"
        "<tr>"
        "<th>שעה</th>"
        "<th>Session ID</th>"
        "<th>סיום שיחה</th>"
        "<th>רמת דחיפות</th>"
        "<th>נושא פניה</th>"
        "<th>הפניה</th>"
        "<th>בקשה לנציגה</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
    )


def fetch_conversations_for_period(
    start_utc: datetime,
    end_utc: datetime,
    local_tz_name: str,
) -> list[dict[str, Any]]:
    """Fetch extraction rows for the requested UTC period."""
    from zoneinfo import ZoneInfo

    local_tz = ZoneInfo(local_tz_name)
    results: list[dict[str, Any]] = []

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT session_id, extraction, metadata, created_at
                FROM extractions
                WHERE created_at >= %s AND created_at < %s
                ORDER BY created_at DESC
                """,
                (start_utc, end_utc),
            )
            rows = cur.fetchall()

    for session_id, extraction, metadata, created_at in rows:
        fields = _extract_fields(extraction)
        created_local = created_at.astimezone(local_tz)
        results.append(
            {
                "session_id": session_id,
                "fields": fields,
                "metadata": metadata if isinstance(metadata, dict) else {},
                "created_at": created_at,
                "created_local": created_local,
            }
        )

    return results


def build_daily_summary_email(
    rows: list[dict[str, Any]],
    report_start_local: datetime,
    report_end_local: datetime,
) -> str:
    """Build HTML email grouped by requested priority rules."""
    priority_rows: list[dict[str, Any]] = []
    remaining_rows: list[dict[str, Any]] = []

    for item in rows:
        fields = item["fields"]
        ending = fields.get("conversation_ending")
        urgency = fields.get("urgency_level")
        is_priority = ending == PRIORITY_ENDING or urgency in PRIORITY_URGENCIES
        if is_priority:
            priority_rows.append(item)
        else:
            remaining_rows.append(item)

    priority_rows.sort(
        key=lambda x: (_urgency_sort_key(x["fields"].get("urgency_level")), x["created_at"]),
        reverse=False,
    )

    grouped_remaining: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in remaining_rows:
        grouped_remaining[item["fields"].get("urgency_level") or "לא ידוע"].append(item)

    for urgency_value in grouped_remaining:
        grouped_remaining[urgency_value].sort(key=lambda x: x["created_at"], reverse=True)

    urgency_groups = sorted(grouped_remaining.keys(), key=_urgency_sort_key)

    period_text = (
        f"{report_start_local.strftime('%Y-%m-%d %H:%M')}"
        f" עד "
        f"{report_end_local.strftime('%Y-%m-%d %H:%M')}"
    )

    html = [
        "<html><body style='font-family:Arial,sans-serif;'>",
        "<h2>סיכום יומי של שיחות</h2>",
        f"<p><strong>טווח הדוח:</strong> {period_text} (שעון ישראל)</p>",
        f"<p><strong>סה\"כ שיחות:</strong> {len(rows)}</p>",
        f"<p><strong>שיחות עדיפות:</strong> {len(priority_rows)}</p>",
        "<hr/>",
        "<h3>1) שיחות עדיפות (נציגה תחזור / דחיפות גבוהה או חירום)</h3>",
        _build_table(priority_rows),
        "<hr/>",
        "<h3>2) יתר השיחות לפי רמת דחיפות</h3>",
    ]

    if not urgency_groups:
        html.append("<p>אין שיחות נוספות מעבר לשיחות העדיפות.</p>")
    else:
        for urgency in urgency_groups:
            html.append(f"<h4>{urgency}</h4>")
            html.append(_build_table(grouped_remaining[urgency]))

    html.append("</body></html>")
    return "".join(html)


def _validate_email_config() -> tuple[bool, str]:
    missing = []
    if not EmailSummaryConfig.CONNECTION_STRING:
        missing.append("COMMUNICATION_SERVICES_CONNECTION_STRING")
    if not EmailSummaryConfig.SENDER_ADDRESS:
        missing.append("MAIL_DOMAIN_NAME")

    if missing:
        return False, f"Missing email settings: {', '.join(missing)}"
    return True, ""


def send_daily_conversation_summary(now_utc: datetime | None = None) -> bool:
    """Generate and send the daily summary email via Azure Communication Services."""
    if not EmailSummaryConfig.ENABLED:
        logger.info("Daily summary mail is disabled.")
        return False

    ok, message = _validate_email_config()
    if not ok:
        logger.warning("Daily summary mail skipped. %s", message)
        return False

    from zoneinfo import ZoneInfo

    local_tz = ZoneInfo(EmailSummaryConfig.TIMEZONE)
    now_utc = now_utc or datetime.now(timezone.utc)
    now_local = now_utc.astimezone(local_tz)
    start_local = now_local - timedelta(days=1)

    rows = fetch_conversations_for_period(start_local.astimezone(timezone.utc), now_utc, EmailSummaryConfig.TIMEZONE)

    html_body = build_daily_summary_email(rows, start_local, now_local)

    subject = f"סיכום שיחות יומי - {now_local.strftime('%Y-%m-%d')}"

    email_client = EmailClient.from_connection_string(EmailSummaryConfig.CONNECTION_STRING)
    email_message = {
        "senderAddress": EmailSummaryConfig.SENDER_ADDRESS,
        "content": {
            "subject": subject,
            "html": html_body,
        },
        "recipients": {
            "to": [{"address": EmailSummaryConfig.RECIPIENT}],
        },
    }

    poller = email_client.begin_send(email_message)
    result = poller.result()

    status = result.get("status") if isinstance(result, dict) else result
    logger.info(
        "Daily summary mail sent to %s with %s conversations (status=%s)",
        EmailSummaryConfig.RECIPIENT,
        len(rows),
        status,
    )
    return True
