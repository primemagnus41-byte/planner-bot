from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def to_utc(dt: datetime, tz_str: str) -> datetime:
    try:
        user_tz = ZoneInfo(tz_str)
    except Exception:
        user_tz = ZoneInfo("Asia/Tashkent")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=user_tz)
    return dt.astimezone(timezone.utc)


def from_utc(dt: datetime, tz_str: str) -> datetime:
    try:
        user_tz = ZoneInfo(tz_str)
    except Exception:
        user_tz = ZoneInfo("Asia/Tashkent")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(user_tz)


def ensure_utc(dt: datetime | None) -> datetime:
    """Offset-naive va offset-aware datetimelarni xavfsiz UTC ga o'tkazadi."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
