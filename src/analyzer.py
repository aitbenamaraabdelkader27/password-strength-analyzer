"""Public orchestration API for password analysis."""

from __future__ import annotations

from typing import TypedDict

from .patterns import PatternFindings, analyze_patterns
from .recommendations import build_issues, build_recommendations
from .scoring import calculate_score, estimate_entropy, strength_level


class AnalysisResult(TypedDict):
    """JSON-compatible analysis result that intentionally excludes the password."""

    score: int
    strength: str
    entropy: float
    checks: dict[str, bool]
    issues: list[str]
    recommendations: list[str]
    patterns: dict[str, bool]


def _build_checks(password: str) -> dict[str, bool]:
    length = len(password)
    return {
        "length": length >= 12,
        "length_8": length >= 8,
        "length_12": length >= 12,
        "length_16": length >= 16,
        "length_20": length >= 20,
        "lowercase": any(character.islower() for character in password),
        "uppercase": any(character.isupper() for character in password),
        "digit": any(character.isdigit() for character in password),
        "special": any(not character.isalnum() for character in password),
    }


def _public_pattern_summary(patterns: PatternFindings) -> dict[str, bool]:
    return {
        "common_password": patterns["is_common_password"],
        "common_word": bool(patterns["weak_words"]),
        "sequence": bool(patterns["sequences"]),
        "repetition": bool(patterns["repetitions"]),
        "year": bool(patterns["years"]),
    }


def analyze_password(password: str) -> AnalysisResult:
    """Analyze one password in memory and return derived findings only."""
    checks = _build_checks(password)
    patterns = analyze_patterns(password)
    entropy = estimate_entropy(password)
    score = calculate_score(password, checks, patterns, entropy)
    return {
        "score": score,
        "strength": strength_level(score),
        "entropy": entropy,
        "checks": checks,
        "issues": build_issues(patterns),
        "recommendations": build_recommendations(len(password), checks, patterns),
        "patterns": _public_pattern_summary(patterns),
    }
