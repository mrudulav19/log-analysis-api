
from datetime import datetime

from app.services.log_parser import parse_line, parse_lines


def test_parse_valid_log_line():
    line = (
        "2026-10-28 09:16:45 ERROR "
        "database Connection timeout"
    )

    result = parse_line(line)

    assert result is not None
    assert result["level"] == "ERROR"
    assert result["source"] == "database"
    assert result["message"] == "Connection timeout"
    assert result["timestamp"] == datetime(2026, 10, 28, 9, 16, 45)


def test_parse_invalid_line():
    assert parse_line("This is invalid") is None


def test_parse_lines_counts():
    lines = [
        "2026-10-28 09:15:21 INFO auth_service Login successful",
        "invalid line",
    ]

    result = parse_lines(lines)

    assert result["total_lines"] == 2
    assert result["parsed_lines"] == 1
    assert result["failed_lines"] == 1
    assert result["invalid_entries"][0]["line_number"] == 2


def test_invalid_calendar_date():
    line = (
        "2026-02-30 09:16:45 ERROR "
        "database Connection timeout"
    )

    assert parse_line(line) is None
