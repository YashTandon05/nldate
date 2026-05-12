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


def test_day_after_tomorrow() -> None:
    assert parse("the day after tomorrow", today=date(2026, 5, 11)) == date(2026, 5, 13)


def test_next_tuesday() -> None:
    assert parse("next Tuesday", today=date(2026, 5, 11)) == date(2026, 5, 12)


def test_last_friday() -> None:
    assert parse("last Friday", today=date(2026, 5, 11)) == date(2026, 5, 8)


def test_month_day_year() -> None:
    assert parse("May 11th, 2026") == date(2026, 5, 11)


def test_year_month_day() -> None:
    assert parse("2026-05-11") == date(2026, 5, 11)


def test_year_month_day_slashes() -> None:
    assert parse("2026/05/11") == date(2026, 5, 11)


def test_abbreviated_month_with_period() -> None:
    assert parse("May. 11, 2026") == date(2026, 5, 11)


def test_two_weeks_from_now() -> None:
    assert parse("2 weeks from now", today=date(2026, 5, 11)) == date(2026, 5, 25)


def test_compound_duration_before_date() -> None:
    assert parse("2 years, 3 months before Dec. 1, 2025") == date(2023, 9, 1)


def test_compound_duration_after_yesterday() -> None:
    assert parse(
        "1 year and 2 months after yesterday", today=date(2025, 12, 1)
    ) == date(2027, 1, 30)


def test_bad_input() -> None:
    with pytest.raises(ValueError):
        parse("banana calendar magic")
