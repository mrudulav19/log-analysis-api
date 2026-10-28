
from app.services.log_parser import parse_lines


sample_logs = [
    "2026-10-28 09:15:21 INFO auth_service User login successful",
    "2026-10-28 09:16:45 ERROR database Connection timeout",
    "This is not a valid log line",
]

result = parse_lines(sample_logs)

print("Total:", result["total_lines"])
print("Parsed:", result["parsed_lines"])
print("Failed:", result["failed_lines"])

for entry in result["entries"]:
    print(entry)
