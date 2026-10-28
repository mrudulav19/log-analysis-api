
import re
from datetime import datetime


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}) "
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL) "
    r"(?P<source>\S+) "
    r"(?P<message>.+)$"
)

VALID_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def parse_line(line):
    """Parse one log line into structured data."""

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            data["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return None

    if data["level"] not in VALID_LEVELS:
        return None

    return {
        "timestamp": timestamp,
        "level": data["level"],
        "source": data["source"],
        "message": data["message"],
        "raw_line": line.rstrip("\r\n"),
    }


def parse_lines(lines):
    """Parse multiple lines and track invalid entries."""

    entries = []
    failed_lines = []

    for line_number, line in enumerate(lines, start=1):
        entry = parse_line(line)

        if entry is None:
            failed_lines.append({
                "line_number": line_number,
                "raw_line": line.rstrip("\r\n"),
            })
        else:
            entry["line_number"] = line_number
            entries.append(entry)

    return {
        "total_lines": len(entries) + len(failed_lines),
        "parsed_lines": len(entries),
        "failed_lines": len(failed_lines),
        "entries": entries,
        "invalid_entries": failed_lines,
    }
