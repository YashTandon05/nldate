from datetime import date
import pytest
from nldate import parse


def test_today() -> None:
    assert parse("today", today=date(2026, 5, 11)) == date(2026, 5, 11)


def test_tomorrow() -> None:
    assert parse("tomorrow", today=date(2026, 5, 11)) == date(2026, 5, 12)


def test_yesterday() -> None:
    assert parse("yesterday", today=date(2026, 5, 11)) == date(2026, 5, 10)


def test_in_three_days() -> None:
    assert parse("in 3 days", today=date(2026, 5, 11)) == date(2026, 5, 14)


def test_three_days_ago() -> None:
    assert parse("3 days ago", today=date(2026, 5, 11)) == date(2026, 5, 8)


def test_five_days_before_specific_date() -> None:
    assert parse("5 days before May 11th, 2026") == date(2026, 5, 6)


def test_two_weeks_from_tomorrow() -> None:
    assert parse("two weeks from tomorrow", today=date(2026, 5, 11)) == date(
        2026, 5, 26
    )


def test_next_tuesday() -> None:
    assert parse("next Tuesday", today=date(2026, 5, 11)) == date(2026, 5, 12)


def test_last_friday() -> None:
    assert parse("last Friday", today=date(2026, 5, 11)) == date(2026, 5, 8)


def test_month_day_year() -> None:
    assert parse("May 11th, 2026") == date(2026, 5, 11)


def test_year_month_day() -> None:
    assert parse("2026-05-11") == date(2026, 5, 11)


def test_year_month_day_slashes() -> None:
    assert parse("2025/12/04") == date(2025, 12, 4)


def test_bad_input() -> None:
    with pytest.raises(ValueError):
        parse("banana calendar magic")
