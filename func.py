from datetime import datetime

def parse_log_line(line: str) -> tuple[datetime, str, str] | None:
    parts = line.split()
    if len(parts) < 4:
        return None
    timestamp_text = " ".join(parts[:2])

    try:
        timestamp = datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

    level = parts[2]
    message = " ".join(parts[3:])
    return (timestamp, level, message)

print(parse_log_line("2026-11-05 14:20:10 WARNING disk space running low"))
print(parse_log_line("2026-11-05 14:20:10 WARNING"))