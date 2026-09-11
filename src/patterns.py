"""Detection of predictable patterns in passwords."""

from __future__ import annotations

import re
from typing import TypedDict

COMMON_PASSWORDS = frozenset({
    "123456", "12345678", "123456789", "admin", "administrator",
    "azerty", "iloveyou", "letmein", "password", "password123",
    "qwerty", "welcome",
})
WEAK_WORDS = (
    "administrator", "password", "welcome", "admin", "azerty",
    "qwerty", "login", "user",
)
# Four-character minimum avoids penalizing short coincidences like "abc".
SEQUENCE_SOURCES = (
    "0123456789", "9876543210",
    "abcdefghijklmnopqrstuvwxyz", "zyxwvutsrqponmlkjihgfedcba",
    "qwertyuiop", "poiuytrewq", "azertyuiop", "poiuytreza",
)
SAME_CHARACTER_RE = re.compile(r"(.)\1{2,}", re.IGNORECASE)
REPEATED_BLOCK_RE = re.compile(r"(.{2,4})\1{2,}", re.IGNORECASE)
YEAR_RE = re.compile(r"(?<!\d)(?:19\d{2}|20\d{2})(?!\d)")


class PatternFindings(TypedDict):
    """Structured pattern signals consumed by the scoring layer."""

    is_common_password: bool
    weak_words: list[str]
    sequences: list[str]
    repetitions: list[str]
    years: list[str]


def find_sequences(password: str, minimum_length: int = 4) -> list[str]:
    """Return distinct predictable sequences, preferring the longest match."""
    normalized = password.casefold()
    matches: set[str] = set()
    for start in range(len(normalized)):
        longest = ""
        for end in range(start + minimum_length, len(normalized) + 1):
            candidate = normalized[start:end]
            if any(candidate in source for source in SEQUENCE_SOURCES):
                longest = candidate
            else:
                break
        if longest:
            matches.add(longest)
    return sorted(
        (
            match for match in matches
            if not any(match != other and match in other for other in matches)
        ),
        key=lambda value: (-len(value), value),
    )


def find_repetitions(password: str) -> list[str]:
    """Return repeated single characters and repeated short blocks."""
    matches = {
        match.group(0).casefold()
        for match in SAME_CHARACTER_RE.finditer(password)
    }
    matches.update(
        match.group(0).casefold()
        for match in REPEATED_BLOCK_RE.finditer(password)
    )
    return sorted(matches, key=lambda value: (-len(value), value))


def find_weak_words(password: str) -> list[str]:
    """Find known weak components using case-insensitive matching."""
    normalized = password.casefold()
    return [word for word in WEAK_WORDS if word in normalized]


def find_years(password: str) -> list[str]:
    """Find standalone four-digit years from 1900 through 2099."""
    return list(dict.fromkeys(YEAR_RE.findall(password)))


def analyze_patterns(password: str) -> PatternFindings:
    """Collect all supported predictability signals for a password."""
    return {
        "is_common_password": password.casefold() in COMMON_PASSWORDS,
        "weak_words": find_weak_words(password),
        "sequences": find_sequences(password),
        "repetitions": find_repetitions(password),
        "years": find_years(password),
    }
