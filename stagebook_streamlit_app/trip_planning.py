"""Pure itinerary calculations and portable iCalendar export."""
from datetime import datetime, timedelta, timezone
from math import isfinite

SHANGHAI = timezone(timedelta(hours=8))
TRANSPORT_BUFFER = {"subway": 15, "bus": 20, "taxi": 10, "walk": 5}


def departure_time(start: datetime, transport: str | None, minutes: float | None,
                   extra_minutes: int = 0) -> datetime | None:
    """Use the displayed route; unknown travel times must remain unknown."""
    if minutes is None or not isfinite(float(minutes)) or minutes < 0:
        return None
    if extra_minutes < 0:
        raise ValueError("额外预留时间不能为负数。")
    return start - timedelta(minutes=float(minutes) + TRANSPORT_BUFFER.get(transport, 10) + extra_minutes)


def schedule_conflicts(events: list[dict], transfer_minutes: int = 60) -> list[dict]:
    """Find all overlaps, including nested shows, and short inter-theater gaps.

    Transfer time is a user-selected allowance, not a real routing estimate.
    """
    if transfer_minutes < 0:
        raise ValueError("转场预留时间不能为负数。")
    result = []
    ordered = sorted(events, key=lambda event: (event["start_time"], event["performance_id"]))
    for i, first in enumerate(ordered):
        for second in ordered[i + 1:]:
            gap = (second["start_time"] - first["end_time"]).total_seconds() / 60
            if gap >= transfer_minutes:
                break
            if gap < 0 or first["theater_id"] != second["theater_id"]:
                result.append({"first": first, "second": second, "gap_minutes": gap,
                               "kind": "overlap" if gap < 0 else "transfer"})
    return result


def _escape(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def _fold(line: str) -> str:
    """Fold at 75 UTF-8 octets without splitting a multibyte character."""
    parts, current = [], ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            parts.append(current)
            current = " "
        current += char
    parts.append(current)
    return "\r\n".join(parts)


def _utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=SHANGHAI)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_calendar(events: list[dict], user_id: int, *, now: datetime | None = None) -> bytes:
    """Export show times (Asia/Shanghai) as UTC with stable per-user UIDs."""
    stamp = _utc(now or datetime.now(timezone.utc))
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//StageBook//Trip Planner//ZH", "CALSCALE:GREGORIAN"]
    for event in events:
        lines.extend([
            "BEGIN:VEVENT", f"UID:{int(user_id)}-{int(event['performance_id'])}@stagebook.local",
            f"DTSTAMP:{stamp}", f"DTSTART:{_utc(event['start_time'])}", f"DTEND:{_utc(event['end_time'])}",
            f"SUMMARY:{_escape(event['title'])}", f"LOCATION:{_escape(event['theater_name'])}",
            f"DESCRIPTION:{_escape('StageBook 观演计划；请提前到场。')}", "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return ("\r\n".join(_fold(line) for line in lines) + "\r\n").encode("utf-8")
