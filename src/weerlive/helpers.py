"""Weerlive API helper functions."""

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from .const import API_TIMEZONE

TIME_PARTS_COUNT = 2


def str_to_datetime(date_str: str, format_str: str) -> datetime | None:
    """Convert a date string in a given format to a datetime object taking API_TIMEZONE into account."""
    if not date_str or date_str == "-":
        return None

    return datetime.strptime(date_str, format_str).replace(tzinfo=ZoneInfo(API_TIMEZONE))


def time_to_datetime(time: str) -> datetime | None:
    """Convert a time string in HH:MM format to a datetime object taking API_TIMEZONE into account."""
    if not time:
        return None

    time_parts = time.split(":")
    if len(time_parts) != TIME_PARTS_COUNT:
        return None

    try:
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        now = datetime.now(ZoneInfo(API_TIMEZONE))
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except ValueError:
        return None


def api_error_message(response_text: str) -> str | None:
    """Return the error message when the API responds with `{"liveweer": [{"fout": "..."}]}` instead of weather data."""
    if '"fout"' not in response_text:
        return None
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        return None
    live = data.get("liveweer") if isinstance(data, dict) else None
    if isinstance(live, list) and live and isinstance(live[0], dict) and "fout" in live[0]:
        return str(live[0]["fout"])
    return None
