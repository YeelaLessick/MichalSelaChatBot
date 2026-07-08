"""Background scheduler for daily conversation summary email."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

from config import EmailSummaryConfig
from mail_service import send_daily_conversation_summary

logger = logging.getLogger(__name__)

_scheduler_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _seconds_until_next_run(now_local: datetime, hour: int, minute: int) -> float:
    target = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now_local >= target:
        target = target + timedelta(days=1)
    return (target - now_local).total_seconds()


def _scheduler_loop() -> None:
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(EmailSummaryConfig.TIMEZONE)

    while not _stop_event.is_set():
        now_local = datetime.now(tz)
        wait_seconds = _seconds_until_next_run(now_local, EmailSummaryConfig.SEND_HOUR, EmailSummaryConfig.SEND_MINUTE)
        next_run = now_local + timedelta(seconds=wait_seconds)

        logger.info(
            "Daily summary scheduler armed. Next run at %s (%s)",
            next_run.strftime("%Y-%m-%d %H:%M:%S"),
            EmailSummaryConfig.TIMEZONE,
        )

        if _stop_event.wait(wait_seconds):
            break

        try:
            send_daily_conversation_summary()
        except Exception as exc:
            logger.exception("Daily summary scheduler run failed: %s", exc)


def start_daily_summary_scheduler() -> None:
    global _scheduler_thread

    if not EmailSummaryConfig.ENABLED:
        logger.info("Daily summary scheduler is disabled by config.")
        return

    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.info("Daily summary scheduler already running.")
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(target=_scheduler_loop, name="daily-summary-scheduler", daemon=True)
    _scheduler_thread.start()
    logger.info(
        "Daily summary scheduler started for %02d:%02d %s",
        EmailSummaryConfig.SEND_HOUR,
        EmailSummaryConfig.SEND_MINUTE,
        EmailSummaryConfig.TIMEZONE,
    )


def stop_daily_summary_scheduler() -> None:
    if _scheduler_thread and _scheduler_thread.is_alive():
        _stop_event.set()
