from datetime import datetime, timedelta, timezone

EVENT_TIMEZONE = timezone(timedelta(hours=5, minutes=30), name="IST")
EVENT_DATE_FORMAT = "%Y-%m-%d %H:%M"


def current_event_time():
    return datetime.now(EVENT_TIMEZONE).strftime(EVENT_DATE_FORMAT)


def parse_event_time(value):
    for date_format in (EVENT_DATE_FORMAT, "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(value, date_format).replace(tzinfo=EVENT_TIMEZONE)
        except (TypeError, ValueError):
            continue
    raise ValueError("Event time must use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM format")


def normalize_event_time(value):
    return parse_event_time(value).strftime(EVENT_DATE_FORMAT)


def format_event_time(value):
    try:
        parsed = parse_event_time(value)
        return parsed.strftime("%a, %d %b %Y at %I:%M %p IST")
    except (TypeError, ValueError):
        return value
