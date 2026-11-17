from datetime import datetime, timedelta, timezone

import pytest
from icalendar import Calendar
from trip_planning import departure_time, schedule_conflicts, export_calendar


def event(pid, start="2026-12-01 19:30", end="2026-12-01 21:30", theater=1, title="剧场之夜"):
    return dict(performance_id=pid, title=title, theater_id=theater, theater_name="上海剧场",
                start_time=datetime.fromisoformat(start), end_time=datetime.fromisoformat(end))


@pytest.mark.parametrize("mode,buffer", [("subway", 15), ("bus", 20), ("taxi", 10), ("walk", 5)])
def test_departure_uses_route_and_extra_time(mode, buffer):
    start = datetime(2026, 12, 1, 0, 10)
    assert departure_time(start, mode, 30, 60) == start - timedelta(minutes=90 + buffer)


@pytest.mark.parametrize("minutes", [None, float("nan"), -1, float("inf")])
def test_missing_transport_has_no_fabricated_departure(minutes):
    assert departure_time(datetime(2026, 12, 1), None, minutes) is None


def test_nested_overlaps_are_all_reported():
    events = [event(1, end="2026-12-01 23:00"), event(2, end="2026-12-01 20:00"),
              event(3, start="2026-12-01 21:00", end="2026-12-01 22:00")]
    conflicts = schedule_conflicts(events)
    assert [(c["first"]["performance_id"], c["second"]["performance_id"]) for c in conflicts] == [(1, 2), (1, 3)]


def test_transfer_threshold_and_same_theater():
    first = event(1)
    assert not schedule_conflicts([first, event(2, start="2026-12-01 21:30", end="2026-12-01 23:00")])
    conflict = schedule_conflicts([first, event(2, start="2026-12-01 22:00", end="2026-12-01 23:00", theater=2)])
    assert conflict[0]["kind"] == "transfer"
    assert conflict[0]["gap_minutes"] == 30
    assert not schedule_conflicts([first, event(2, start="2026-12-01 22:30", end="2026-12-01 23:30", theater=2)])


def test_ics_timezone_escaping_folding_and_stable_uid():
    title = "中文剧目" * 30 + ",;\\\n第二行"
    events = [event(17, title=title)]
    data = export_calendar(events, 5, now=datetime(2026, 11, 17, tzinfo=timezone.utc))
    assert all(len(line) <= 75 for line in data.split(b"\r\n"))
    unfolded = data.decode().replace("\r\n ", "")
    assert "DTSTART:20261201T113000Z" in unfolded
    assert "DTEND:20261201T133000Z" in unfolded
    assert "UID:5-17@stagebook.local" in unfolded
    assert "\\,\\;\\\\\\n第二行" in unfolded
    assert unfolded.count("BEGIN:VEVENT") == 1
    assert data.endswith(b"END:VCALENDAR\r\n")
    parsed = Calendar.from_ical(data).walk("VEVENT")[0]
    assert str(parsed["summary"]) == title
    assert parsed.decoded("dtstart") == datetime(2026, 12, 1, 11, 30, tzinfo=timezone.utc)


def test_empty_calendar_and_invalid_allowance():
    assert b"BEGIN:VEVENT" not in export_calendar([], 1)
    with pytest.raises(ValueError):
        schedule_conflicts([], -1)
