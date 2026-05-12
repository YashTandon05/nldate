from __future__ import annotations

import calendar
import re
from datetime import date, timedelta


MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "a": 1,
    "an": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def parse(s: str, today: date | None = None) -> date:
    reference = today or date.today()
    text = _normalize(s)

    simple = {
        "today": reference,
        "tomorrow": reference + timedelta(days=1),
        "yesterday": reference - timedelta(days=1),
    }
    if text in simple:
        return simple[text]

    absolute = _parse_absolute(text, reference)
    if absolute is not None:
        return absolute

    weekday = _parse_weekday(text, reference)
    if weekday is not None:
        return weekday

    relative = _parse_relative(text, reference)
    if relative is not None:
        return relative

    before_after = _parse_before_after(text, reference)
    if before_after is not None:
        return before_after

    raise ValueError(f"Could not parse date: {s!r}")


def _normalize(s: str) -> str:
    text = s.strip().lower()

    # Remove ordinal suffixes: 1st -> 1
    text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", text)

    # Remove punctuation commonly used in dates
    text = text.replace(",", "")
    text = text.replace(".", "")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def _parse_number(token: str) -> int:
    if token.isdigit():
        return int(token)
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    raise ValueError(f"Invalid number: {token}")


def _parse_absolute(text: str, reference: date) -> date | None:
    iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if iso:
        year, month, day = map(int, iso.groups())
        return date(year, month, day)

    slash_iso = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
    if slash_iso:
        year, month, day = map(int, slash_iso.groups())
        return date(year, month, day)

    numeric = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", text)
    if numeric:
        month, day, year = map(int, numeric.groups())
        if year < 100:
            year += 2000
        return date(year, month, day)

    month_day_year = re.fullmatch(r"([a-z]+) (\d{1,2}) (\d{4})", text)
    if month_day_year and month_day_year.group(1) in MONTHS:
        month_name, day_text, year_text = month_day_year.groups()
        return date(int(year_text), MONTHS[month_name], int(day_text))

    month_day = re.fullmatch(r"([a-z]+) (\d{1,2})", text)
    if month_day and month_day.group(1) in MONTHS:
        month_name, day_text = month_day.groups()
        return date(reference.year, MONTHS[month_name], int(day_text))

    return None


def _parse_weekday(text: str, reference: date) -> date | None:
    match = re.fullmatch(r"(next|last|this) ([a-z]+)", text)
    if not match:
        return None

    direction, weekday_name = match.groups()
    if weekday_name not in WEEKDAYS:
        return None

    target = WEEKDAYS[weekday_name]
    current = reference.weekday()

    if direction == "next":
        days = (target - current) % 7
        return reference + timedelta(days=days or 7)

    if direction == "last":
        days = (current - target) % 7
        return reference - timedelta(days=days or 7)

    days = (target - current) % 7
    return reference + timedelta(days=days)


def _parse_relative(text: str, reference: date) -> date | None:
    match = re.fullmatch(
        r"(?:in )?([a-z0-9]+) (day|days|week|weeks|month|months|year|years)", text
    )
    if match:
        amount_text, unit = match.groups()
        return _add(reference, _parse_number(amount_text), unit)

    match = re.fullmatch(
        r"([a-z0-9]+) (day|days|week|weeks|month|months|year|years) ago", text
    )
    if match:
        amount_text, unit = match.groups()
        return _add(reference, -_parse_number(amount_text), unit)

    match = re.fullmatch(
        r"([a-z0-9]+) (day|days|week|weeks|month|months|year|years) from (today|tomorrow|yesterday)",
        text,
    )
    if match:
        amount_text, unit, base_text = match.groups()
        base = parse(base_text, today=reference)
        return _add(base, _parse_number(amount_text), unit)

    return None


def _parse_before_after(text: str, reference: date) -> date | None:
    match = re.fullmatch(
        r"([a-z0-9]+) (day|days|week|weeks|month|months|year|years) "
        r"(before|after|from) (.+)",
        text,
    )
    if not match:
        return None

    amount_text, unit, direction, base_text = match.groups()
    base = parse(base_text, today=reference)
    amount = _parse_number(amount_text)

    if direction == "before":
        amount = -amount

    return _add(base, amount, unit)


def _add(base: date, amount: int, unit: str) -> date:
    if unit.startswith("day"):
        return base + timedelta(days=amount)

    if unit.startswith("week"):
        return base + timedelta(weeks=amount)

    if unit.startswith("month"):
        return _add_months(base, amount)

    if unit.startswith("year"):
        return _add_months(base, amount * 12)

    raise ValueError(f"Unsupported unit: {unit}")


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
