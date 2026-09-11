"""Conservative heuristics for user-specific password predictability."""

from __future__ import annotations

import re
from typing import Any, TypedDict

SEPARATOR_RE = re.compile(r"[^a-z0-9]+")
USERNAME_SPLIT_RE = re.compile(r"[^a-z0-9]+")
TRAILING_SYMBOL_RE = re.compile(r"[!@#$%&*?._-]+$")
DIGIT_RE = re.compile(r"\d+")


class PersonalProfile(TypedDict):
    """Validated optional profile fields used for one analysis only."""

    first_name: str
    last_name: str
    username: str
    birth_year: str
    keywords: list[str]


class PersonalizedResult(TypedDict):
    """Derived personalized findings; source values are deliberately absent."""

    risk: str
    penalty: int
    matched_fields: list[str]
    detected_patterns: list[str]
    penalty_explanations: list[str]
    recommendations: list[str]


def _compact(value: str) -> str:
    """Case-fold and remove simple separators for practical comparisons."""
    return SEPARATOR_RE.sub("", value.casefold())


def _username_tokens(username: str) -> list[str]:
    """Return conservative username parts, excluding short coincidences."""
    normalized = username.casefold()
    parts = [part for part in USERNAME_SPLIT_RE.split(normalized) if len(part) >= 3]
    compact = _compact(username)
    if len(compact) >= 3 and compact not in parts:
        parts.append(compact)
    return parts


def analyze_personal_predictability(
    password: str, profile: PersonalProfile
) -> PersonalizedResult:
    """Assess obvious links between a password and optional profile data."""
    compact_password = _compact(password)
    matched_fields: list[str] = []
    patterns: list[str] = []
    explanations: list[str] = []
    penalty = 0
    matched_personal_tokens: list[str] = []

    field_specs = (
        ("first_name", "first name", 16),
        ("last_name", "last name", 16),
    )
    for key, label, points in field_specs:
        token = _compact(profile[key])
        if len(token) >= 3 and token in compact_password:
            matched_fields.append(key)
            matched_personal_tokens.append(token)
            patterns.append(f"Contains your {label}.")
            explanations.append(f"-{points}: matched {label}")
            penalty += points

    username_matches = [
        token for token in _username_tokens(profile["username"])
        if token in compact_password
    ]
    if username_matches:
        matched_fields.append("username")
        matched_personal_tokens.extend(username_matches)
        patterns.append("Contains a meaningful fragment of your username.")
        explanations.append("-14: matched username fragment")
        penalty += 14

    keyword_match = False
    for keyword in profile["keywords"]:
        token = _compact(keyword)
        if len(token) >= 3 and token in compact_password:
            keyword_match = True
            matched_personal_tokens.append(token)
    if keyword_match:
        matched_fields.append("keywords")
        patterns.append("Contains one or more personal keywords.")
        explanations.append("-12: matched personal keyword")
        penalty += 12

    has_personal_token = bool(matched_personal_tokens)
    birth_year = profile["birth_year"]
    short_year = birth_year[-2:] if birth_year else ""
    year_match = bool(
        birth_year
        and (birth_year in password or (has_personal_token and short_year in password))
    )
    if year_match:
        matched_fields.append("birth_year")
        patterns.append("Contains your birth year.")
        explanations.append("-12: matched birth year")
        penalty += 12

    if has_personal_token and year_match:
        patterns.append("Combines personal information with a year.")
        explanations.append("-10: personal token + year structure")
        penalty += 10
    elif has_personal_token and DIGIT_RE.search(password):
        patterns.append("Combines personal information with a number.")
        explanations.append("-6: personal token + number structure")
        penalty += 6

    if has_personal_token and TRAILING_SYMBOL_RE.search(password):
        patterns.append("Adds a predictable symbol suffix to personal information.")
        explanations.append("-5: predictable symbol suffix")
        penalty += 5

    if has_personal_token:
        remainder = compact_password
        for token in sorted(set(matched_personal_tokens), key=len, reverse=True):
            remainder = remainder.replace(token, "")
        if birth_year:
            remainder = remainder.replace(birth_year, "")
        # A password made almost entirely from matched data plus a few digits is
        # especially guessable, even if composition rules make it look complex.
        if not remainder or (remainder.isdigit() and len(remainder) <= 3):
            patterns.append("The password is mostly personal information and formatting.")
            explanations.append("-10: password is dominated by personal data")
            penalty += 10

    penalty = min(60, penalty)
    if penalty == 0:
        risk = "Low"
    elif penalty <= 18:
        risk = "Moderate"
    elif penalty <= 34:
        risk = "High"
    else:
        risk = "Critical"

    recommendations = []
    if penalty:
        recommendations.append(
            "Use a password unrelated to public or easily discoverable information about you."
        )
        if has_personal_token and DIGIT_RE.search(password):
            recommendations.append(
                "Avoid building passwords from a personal word followed by a number or year."
            )
    else:
        recommendations.append(
            "No obvious link to the supplied profile was detected; keep the password unique."
        )

    return {
        "risk": risk,
        "penalty": penalty,
        "matched_fields": matched_fields,
        "detected_patterns": patterns,
        "penalty_explanations": explanations,
        "recommendations": recommendations,
    }


def personalized_assessment(password: str, profile: PersonalProfile) -> dict[str, Any]:
    """Combine technical analysis with a separately reported personal penalty."""
    from .analyzer import analyze_password

    technical = analyze_password(password)
    personal = analyze_personal_predictability(password, profile)
    return {
        "technical": technical,
        "personal_predictability": personal,
        "personalized_score": max(0, technical["score"] - personal["penalty"]),
    }
