
from datetime import date


def calculate_age(dob, today):
    # Calculate completed years based on whether the birthday has passed
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )


def test_age_after_birthday():
    assert calculate_age(
        date(1998, 12, 1),
        date(2026, 12, 2)
    ) == 28


def test_age_before_birthday():
    assert calculate_age(
        date(1998, 12, 1),
        date(2026, 11, 22)
    ) == 27


def test_age_on_birthday():
    assert calculate_age(
        date(1998, 12, 1),
        date(2026, 12, 1)
    ) == 28




def is_stale_member(last_flight_date, today):
    # Match the Snowflake rule: flight date earlier than today minus 90 days
    if last_flight_date is None:
        return None

    return (today - last_flight_date).days > 90


def test_stale_member_over_90_days():
    assert is_stale_member(
        date(2026, 8, 1),
        date(2026, 11, 22)
    ) is True


def test_active_member_within_90_days():
    assert is_stale_member(
        date(2026, 11, 1),
        date(2026, 11, 22)
    ) is False


def test_member_exactly_90_days():
    assert is_stale_member(
        date(2026, 8, 24),
        date(2026, 11, 22)
    ) is False


def test_member_without_flight_date():
    assert is_stale_member(
        None,
        date(2026, 11, 22)
    ) is None





from datetime import datetime


def get_latest_member_record(events):
    # Select the event with the most recent source update timestamp
    return max(events, key=lambda event: event["source_updated_at"])


def test_member_moves_from_india_to_usa():
    events = [
        {
            "global_member_id": "GLOBAL_1001",
            "country": "IND",
            "source_updated_at": datetime(2026, 1, 10, 10, 0)
        },
        {
            "global_member_id": "GLOBAL_1001",
            "country": "USA",
            "source_updated_at": datetime(2026, 6, 15, 14, 30)
        }
    ]

    latest = get_latest_member_record(events)

    assert latest["country"] == "USA"


def test_latest_record_independent_of_input_order():
    events = [
        {
            "global_member_id": "GLOBAL_1001",
            "country": "USA",
            "source_updated_at": datetime(2026, 6, 15, 14, 30)
        },
        {
            "global_member_id": "GLOBAL_1001",
            "country": "IND",
            "source_updated_at": datetime(2026, 1, 10, 10, 0)
        }
    ]

    latest = get_latest_member_record(events)

    assert latest["country"] == "USA"
