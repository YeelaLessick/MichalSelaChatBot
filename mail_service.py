"""Weekly email summary service for conversation extractions."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from azure.communication.email import EmailClient

from config import EmailSummaryConfig
from db import _connect

logger = logging.getLogger(__name__)

# Order in which conversation-ending groups appear in the report.
CONVERSATION_ENDING_ORDER = [
    "נציגה תחזור",
    "נטישה",
    "שיחה הושלמה",
]
UNKNOWN_ENDING = "לא ידוע"

# Human-readable Hebrew labels for the conversation source (channel).
CHANNEL_LABELS = {
    "whatsapp": "וואטסאפ",
    "bot_framework": "צ׳אט",
    "unknown": "לא ידוע",
}


def _format_source(channel: Any) -> str:
    """Map a raw channel value to a readable Hebrew conversation-source label."""
    if not channel:
        return "-"
    key = str(channel).strip().lower()
    return CHANNEL_LABELS.get(key, str(channel))


def _resolve_phone_number(item: dict[str, Any]) -> str:
    """Phone number from metadata, falling back to the whatsapp_ session id."""
    phone = item.get("metadata", {}).get("phone_number")
    if phone and str(phone).strip():
        return str(phone).strip()

    session_id = str(item.get("session_id") or "")
    if session_id.startswith("whatsapp_"):
        raw = session_id[len("whatsapp_"):]
        # Format is whatsapp_{phone}_{uuid8}; drop the optional uuid suffix.
        return raw.rsplit("_", 1)[0] if "_" in raw else raw
    return "-"

# Fields shown for every conversation, in display order (English key -> Hebrew label).
FIELD_LABELS: list[tuple[str, str]] = [
    ("urgency_level", "רמת דחיפות"),
    ("inquiry_subject", "נושא הפניה"),
    ("caller_gender", "מין הפונה"),
    ("caller_age", "גיל הפונה"),
    ("relationship_to_threat", "קרבה לגורם המאיים / לשורדת"),
    ("referred_to", "לאן הפנינו"),
    ("wants_human_callback", "רוצה שנציגה תחזור"),
    ("conversation_time", "זמן השיחה"),
]


def _extract_fields(extraction: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(extraction, dict):
        return {}
    extracted = extraction.get("extracted_fields")
    if isinstance(extracted, dict):
        return extracted
    return extraction


def _format_value(value: Any) -> str:
    if isinstance(value, list):
        values = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(values) if values else "-"
    if value is None:
        return "-"
    text = str(value).strip()
    return text if text else "-"


def _build_conversation_card(item: dict[str, Any]) -> str:
    fields = item["fields"]
    created_local = item["created_local"].strftime("%Y-%m-%d %H:%M")
    source = _format_source(item.get("metadata", {}).get("channel"))
    phone_number = _resolve_phone_number(item)

    detail_rows = "".join(
        (
            "<tr>"
            f"<td style='padding:4px 10px;font-weight:bold;white-space:nowrap;'>{label}</td>"
            f"<td style='padding:4px 10px;'>{_format_value(fields.get(key))}</td>"
            "</tr>"
        )
        for key, label in FIELD_LABELS
    )

    return (
        "<div style='border:1px solid #ccc;border-radius:6px;padding:10px;margin:10px 0;'>"
        f"<p style='margin:0 0 6px;'><strong>מזהה שיחה:</strong> {item['session_id']} "
        f"&nbsp;|&nbsp; <strong>תאריך:</strong> {created_local} "
        f"&nbsp;|&nbsp; <strong>מקור השיחה:</strong> {source} "
        f"&nbsp;|&nbsp; <strong>מספר טלפון:</strong> {phone_number}</p>"
        "<table style='border-collapse:collapse;width:100%;'>"
        f"<tbody>{detail_rows}</tbody>"
        "</table>"
        "</div>"
    )


def _build_group(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<p>אין שיחות בקטגוריה זו.</p>"
    return "".join(_build_conversation_card(item) for item in items)



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


def build_weekly_summary_email(
    rows: list[dict[str, Any]],
    report_start_local: datetime,
    report_end_local: datetime,
) -> str:
    """Build HTML email grouped by how each conversation ended."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in rows:
        ending = item["fields"].get("conversation_ending") or UNKNOWN_ENDING
        grouped[ending].append(item)

    for ending in grouped:
        grouped[ending].sort(key=lambda x: x["created_at"], reverse=True)

    # Preferred order first, then any unexpected endings, then unknown last.
    ordered_endings = [e for e in CONVERSATION_ENDING_ORDER if e in grouped]
    extras = [e for e in grouped if e not in CONVERSATION_ENDING_ORDER and e != UNKNOWN_ENDING]
    ordered_endings.extend(sorted(extras))
    if UNKNOWN_ENDING in grouped:
        ordered_endings.append(UNKNOWN_ENDING)

    period_text = (
        f"{report_start_local.strftime('%Y-%m-%d')}"
        f" עד "
        f"{report_end_local.strftime('%Y-%m-%d')}"
    )

    html = [
        "<html><body dir='rtl' style='font-family:Arial,sans-serif;'>",
        "<h2>סיכום שבועי של שיחות</h2>",
        f"<p><strong>טווח הדוח:</strong> {period_text} (שעון ישראל)</p>",
        f"<p><strong>סה\"כ שיחות:</strong> {len(rows)}</p>",
        "<hr/>",
    ]

    if not ordered_endings:
        html.append("<p>לא נרשמו שיחות בשבוע החולף.</p>")
    else:
        for ending in ordered_endings:
            items = grouped[ending]
            html.append(f"<h3>{ending} ({len(items)})</h3>")
            html.append(_build_group(items))

    html.append("</body></html>")
    return "".join(html)


def _build_transcript_html(messages: list[Any] | None) -> str:
    """Render the raw conversation transcript as HTML, if messages are provided."""
    if not messages:
        return ""

    rows: list[str] = []
    for msg in messages:
        content = str(getattr(msg, "content", "") or "").strip()
        if not content:
            continue
        msg_type = str(getattr(msg, "type", "") or "").strip().lower()
        speaker = "פונה" if msg_type in {"human", "user"} else "בוט"
        rows.append(
            "<tr>"
            f"<td style='padding:4px 10px;font-weight:bold;white-space:nowrap;vertical-align:top;'>{speaker}</td>"
            f"<td style='padding:4px 10px;'>{content}</td>"
            "</tr>"
        )

    if not rows:
        return ""

    return (
        "<h3>תמליל השיחה</h3>"
        "<table style='border-collapse:collapse;width:100%;'>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def build_emergency_callback_email(
    session_id: str,
    fields: dict[str, Any],
    metadata: dict[str, Any] | None,
    messages: list[Any] | None = None,
) -> str:
    """Build the HTML body for an emergency human-callback notification."""
    metadata = metadata if isinstance(metadata, dict) else {}
    phone_number = metadata.get("phone_number") or "-"
    source = _format_source(metadata.get("channel"))

    detail_rows = "".join(
        (
            "<tr>"
            f"<td style='padding:4px 10px;font-weight:bold;white-space:nowrap;'>{label}</td>"
            f"<td style='padding:4px 10px;'>{_format_value(fields.get(key))}</td>"
            "</tr>"
        )
        for key, label in FIELD_LABELS
    )

    transcript_html = _build_transcript_html(messages)

    html = [
        "<html><body dir='rtl' style='font-family:Arial,sans-serif;'>",
        "<h2 style='color:#b00000;'>🚨 בקשה לחזרת נציגה אנושית</h2>",
        "<p>הפונה ביקשה שנציג/ה אנושי/ת יחזור/תחזור אליה. יש לטפל בהקדם.</p>",
        "<table style='border-collapse:collapse;width:100%;'>"
        "<tbody>"
        f"<tr><td style='padding:4px 10px;font-weight:bold;white-space:nowrap;'>מזהה שיחה</td>"
        f"<td style='padding:4px 10px;'>{session_id}</td></tr>"
        f"<tr><td style='padding:4px 10px;font-weight:bold;white-space:nowrap;'>מספר טלפון</td>"
        f"<td style='padding:4px 10px;'>{_format_value(phone_number)}</td></tr>"
        f"<tr><td style='padding:4px 10px;font-weight:bold;white-space:nowrap;'>מקור השיחה</td>"
        f"<td style='padding:4px 10px;'>{source}</td></tr>"
        "</tbody></table>",
        "<hr/>",
        "<h3>פרטי השיחה</h3>",
        "<table style='border-collapse:collapse;width:100%;'>"
        f"<tbody>{detail_rows}</tbody>"
        "</table>",
    ]

    if transcript_html:
        html.append("<hr/>")
        html.append(transcript_html)

    html.append("</body></html>")
    return "".join(html)


def send_emergency_callback_email(
    session_id: str,
    extraction: dict[str, Any] | None,
    session_metadata: dict[str, Any] | None = None,
    messages: list[Any] | None = None,
) -> bool:
    """Send an immediate emergency email because the caller asked for a human.

    Called mid-conversation once the agent has detected that the caller
    requested a human representative.

    Returns True when an email was sent, False otherwise.
    """
    fields = _extract_fields(extraction)

    ok, message = _validate_email_config()
    if not ok:
        logger.warning("Emergency callback mail skipped. %s", message)
        return False

    html_body = build_emergency_callback_email(session_id, fields, session_metadata, messages)
    subject = "🚨 בקשה דחופה לחזרת נציגה אנושית"

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

    meta = session_metadata if isinstance(session_metadata, dict) else {}
    source = _format_source(meta.get("channel"))
    phone_number = _resolve_phone_number({"session_id": session_id, "metadata": meta})
    details = ", ".join(
        f"{label}={_format_value(fields.get(key))}" for key, label in FIELD_LABELS
    )
    logger.info(
        "🚨 Caller asked for a human — emergency mail sent to %s for session %s "
        "(status=%s) | מקור=%s, טלפון=%s, %s",
        EmailSummaryConfig.RECIPIENT,
        session_id,
        status,
        source,
        phone_number,
        details,
    )
    return True


def _validate_email_config() -> tuple[bool, str]:
    missing = []
    if not EmailSummaryConfig.CONNECTION_STRING:
        missing.append("COMMUNICATION_SERVICES_CONNECTION_STRING")
    if not EmailSummaryConfig.SENDER_ADDRESS:
        missing.append("MAIL_DOMAIN_NAME")

    if missing:
        return False, f"Missing email settings: {', '.join(missing)}"
    return True, ""


def send_weekly_conversation_summary(now_utc: datetime | None = None) -> bool:
    """Generate and send the weekly summary email via Azure Communication Services."""
    ok, message = _validate_email_config()
    if not ok:
        logger.warning("Weekly summary mail skipped. %s", message)
        return False

    from zoneinfo import ZoneInfo

    local_tz = ZoneInfo(EmailSummaryConfig.TIMEZONE)
    now_utc = now_utc or datetime.now(timezone.utc)
    now_local = now_utc.astimezone(local_tz)
    start_local = now_local - timedelta(days=7)

    rows = fetch_conversations_for_period(start_local.astimezone(timezone.utc), now_utc, EmailSummaryConfig.TIMEZONE)

    html_body = build_weekly_summary_email(rows, start_local, now_local)

    subject = f"סיכום שיחות שבועי - {now_local.strftime('%Y-%m-%d')}"

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
        "Weekly summary mail sent to %s with %s conversations (status=%s)",
        EmailSummaryConfig.RECIPIENT,
        len(rows),
        status,
    )
    return True
