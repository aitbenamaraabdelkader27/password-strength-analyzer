"""Tests for entropy and score behavior."""

import pytest

from src.analyzer import analyze_password
from src.scoring import estimate_entropy, strength_level


def test_entropy_uses_detected_character_pool() -> None:
    assert estimate_entropy("abcdefgh") == pytest.approx(37.6)
    assert estimate_entropy("Abcdef1!") > estimate_entropy("abcdefgh")


def test_empty_password_entropy_is_zero() -> None:
    assert estimate_entropy("") == 0.0


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "Very Weak"), (19, "Very Weak"), (20, "Weak"),
        (40, "Medium"), (60, "Strong"), (80, "Very Strong"),
        (100, "Very Strong"),
    ],
)
def test_strength_boundaries(score: int, expected: str) -> None:
    assert strength_level(score) == expected


@pytest.mark.parametrize(
    "password",
    ["1", "password", "Admin2026!", "Cobalt7!", "V3ry-L0ng-Random!Passphrase#2026"],
)
def test_scores_are_always_bounded(password: str) -> None:
    assert 0 <= analyze_password(password)["score"] <= 100


def test_strong_password_scores_above_obviously_weak_password() -> None:
    weak = analyze_password("123456")["score"]
    strong = analyze_password("M7!vQ2#kL9@xR4$p")["score"]
    assert strong > weak
    assert strong >= 60


def test_year_penalty_is_moderate() -> None:
    result = analyze_password("Orbit!Canvas#2026")
    assert result["patterns"]["year"] is True
    assert result["score"] >= 40


@pytest.mark.parametrize(
    "password",
    [
        "G7!xP2#vQ9@Lm4$Zr8&Kd1",
        "Mango!River7-Cloud#Falcon92",
        "vQ7!mZ2#Kp9@Ls4&Xr8$Df1*Hw6",
    ],
)
def test_genuinely_strong_passwords_can_reach_the_nineties(password: str) -> None:
    assert analyze_password(password)["score"] >= 90


def test_exceptional_password_can_reach_100() -> None:
    password = "G7!xP2#vQ9@Lm4$Zr8&Kd1*Hw6?Nc3%Bt5^Ys0"
    assert analyze_password(password)["score"] == 100


def test_long_word_based_phrase_is_not_automatically_exceptional() -> None:
    result = analyze_password("Falcon-River-Mango-Orbit-Coffee-47!")
    assert 90 <= result["score"] < 100


def test_random_extra_length_generally_improves_score() -> None:
    short = analyze_password("G7!xP2#vQ9@Lm4$Z")
    long = analyze_password("G7!xP2#vQ9@Lm4$Zr8&Kd1")
    assert long["score"] > short["score"]


def test_patterns_still_reduce_an_otherwise_long_password() -> None:
    clean = analyze_password("G7!xP2#vQ9@Lm4$Zr8&Kd1")
    repeated = analyze_password("G7!xP2#vQ9@Lm4$Zabababab")
    assert repeated["patterns"]["repetition"] is True
    assert repeated["score"] < clean["score"]
