"""Generate focused, actionable security guidance."""

from __future__ import annotations

from typing import Mapping, Sequence


def build_issues(patterns: Mapping[str, bool | Sequence[str]]) -> list[str]:
    """Translate detected patterns into concise issue descriptions."""
    issues: list[str] = []
    if patterns["is_common_password"]:
        issues.append("This is a commonly used password.")
    if patterns["weak_words"]:
        issues.append("Common weak word detected.")
    if patterns["sequences"]:
        issues.append("Predictable sequence detected.")
    if patterns["repetitions"]:
        issues.append("Repeated characters or blocks detected.")
    if patterns["years"]:
        issues.append("A predictable year pattern was detected.")
    return issues


def build_recommendations(
    password_length: int,
    checks: Mapping[str, bool],
    patterns: Mapping[str, bool | Sequence[str]],
) -> list[str]:
    """Return recommendations relevant to the findings."""
    recommendations: list[str] = []
    if password_length < 12:
        recommendations.append(
            "Use at least 12 characters; 16 or more is stronger."
        )
    elif password_length < 16:
        recommendations.append(
            "Consider increasing the password to 16 characters or more."
        )

    diversity_count = sum(
        bool(checks[name])
        for name in ("lowercase", "uppercase", "digit", "special")
    )
    if password_length < 16 and diversity_count < 3:
        recommendations.append(
            "Mix character types or use a longer multi-word passphrase."
        )
    if patterns["is_common_password"]:
        recommendations.append("Choose a unique password that is not commonly used.")
    if patterns["weak_words"]:
        recommendations.append("Avoid common words and account-related terms.")
    if patterns["sequences"]:
        recommendations.append("Avoid keyboard, alphabetic, and numeric sequences.")
    if patterns["repetitions"]:
        recommendations.append("Avoid repeated characters and repeated short patterns.")
    if patterns["years"]:
        recommendations.append(
            "Do not rely on a year as the password's main source of variation."
        )
    if not recommendations:
        recommendations.append(
            "Keep this password unique and store it in a trusted password manager."
        )
    return recommendations
