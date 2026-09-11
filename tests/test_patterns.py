"""Tests for predictable-pattern detection."""

import pytest

from src.patterns import analyze_patterns, find_repetitions, find_sequences, find_years


@pytest.mark.parametrize("password", ["123456", "PASSWORD", "QwErTy", "letmein"])
def test_common_passwords_are_case_insensitive(password: str) -> None:
    assert analyze_patterns(password)["is_common_password"] is True


@pytest.mark.parametrize(
    "password", ["1234x", "x654321y", "ABCD!", "fedcba9", "qwerty!", "azerty7"]
)
def test_predictable_sequences_are_detected(password: str) -> None:
    assert find_sequences(password)


def test_short_coincidences_are_not_sequences() -> None:
    assert find_sequences("safe-abc-word") == []


@pytest.mark.parametrize("password", ["aaaa", "111111", "!!!!!!", "abababab"])
def test_repetitions_are_detected(password: str) -> None:
    assert find_repetitions(password)


def test_common_word_inside_password_is_detected() -> None:
    assert "admin" in analyze_patterns("Admin2026!")["weak_words"]


def test_year_detection_is_bounded() -> None:
    assert find_years("Launch-1999-2026") == ["1999", "2026"]
    assert find_years("x12026y") == []
