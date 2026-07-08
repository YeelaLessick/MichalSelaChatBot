"""Background scheduler for weekly conversation summary email."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

from config import EmailSummaryConfig
from mail_service import send_weekly_conversation_summary

logger = logging.getLogger(__name__)

_scheduler_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _seconds_until_next_run(now_local: datetime, weekday: int, hour: int, minute: int) -> float:
    target = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    days_ahead = (weekday - now_local.weekday()) % 7
    target = target + timedelta(days=days_ahead)
    if now_local >= target:
        target = target + timedelta(days=7)
    return (target - now_local).total_seconds()


def _scheduler_loop() -> None:
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(EmailSummaryConfig.TIMEZONE)

    while not _stop_event.is_set():
        now_local = datetime.now(tz)
        if EmailSummaryConfig.DEBUG_MODE:
            # Fire at the top of the next hour for testing.
            next_run = (now_local + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            wait_seconds = (next_run - now_local).total_seconds()
        else:
            wait_seconds = _seconds_until_next_run(
                now_local,
                EmailSummaryConfig.SEND_WEEKDAY,
                EmailSummaryConfig.SEND_HOUR,
                EmailSummaryConfig.SEND_MINUTE,
            )
            next_run = now_local + timedelta(seconds=wait_seconds)

        logger.info(
            "%s summary scheduler armed. Next run at %s (%s)",
            "DEBUG (hourly)" if EmailSummaryConfig.DEBUG_MODE else "Weekly",
            next_run.strftime("%Y-%m-%d %H:%M:%S"),
            EmailSummaryConfig.TIMEZONE,
        )

        if _stop_event.wait(wait_seconds):
            break

        try:
            send_weekly_conversation_summary()
        except Exception as exc:
            logger.exception("Weekly summary scheduler run failed: %s", exc)


def start_daily_summary_scheduler() -> None:
    global _scheduler_thread

    if not EmailSummaryConfig.ENABLED:
        logger.info("Weekly summary scheduler is disabled by config.")
        return

    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.info("Weekly summary scheduler already running.")
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(target=_scheduler_loop, name="weekly-summary-scheduler", daemon=True)
    _scheduler_thread.start()
    logger.info(
        "Weekly summary scheduler started for weekday %s at %02d:%02d %s",
        EmailSummaryConfig.SEND_WEEKDAY,
        EmailSummaryConfig.SEND_HOUR,
        EmailSummaryConfig.SEND_MINUTE,
        EmailSummaryConfig.TIMEZONE,
    )


def stop_daily_summary_scheduler() -> None:
    if _scheduler_thread and _scheduler_thread.is_alive():
        _stop_event.set()
