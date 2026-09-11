"""Explainable scoring and entropy estimation."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

LEVELS = (
    (20, "Very Weak"), (40, "Weak"), (60, "Medium"),
    (80, "Strong"), (101, "Very Strong"),
)


def character_pool_size(password: str) -> int:
    """Estimate the available character pool based on types in use."""
    pool_size = 0
    if any(character.islower() for character in password):
        pool_size += 26
    if any(character.isupper() for character in password):
        pool_size += 26
    if any(character.isdigit() for character in password):
        pool_size += 10
    if any(not character.isalnum() and character.isascii() for character in password):
        pool_size += 33
    if any(not character.isascii() for character in password):
        pool_size += 100
    return pool_size


def estimate_entropy(password: str) -> float:
    """Return simplified theoretical entropy, rounded to one decimal place."""
    pool_size = character_pool_size(password)
    if not password or pool_size == 0:
        return 0.0
    return round(len(password) * math.log2(pool_size), 1)


def length_points(length: int) -> float:
    """Reward each character while giving longer passwords greater weight."""
    if length < 8:
        return float(length)
    if length < 12:
        return 12.0 + (length - 8) * 2.0
    if length < 16:
        return 22.0 + (length - 12) * 2.0
    if length < 20:
        return 32.0 + (length - 16) * 2.0
    return min(48.0, 42.0 + (length - 20) * 0.5)


def strength_level(score: int) -> str:
    """Map a score to its documented strength band."""
    for upper_bound, label in LEVELS:
        if score < upper_bound:
            return label
    return "Very Strong"


def calculate_score(
    password: str,
    checks: Mapping[str, bool],
    patterns: Mapping[str, bool | Sequence[str]],
    entropy: float,
) -> int:
    """Combine positive properties and explicit predictability penalties."""
    diversity_count = sum(
        bool(checks[name])
        for name in ("lowercase", "uppercase", "digit", "special")
    )
    score = length_points(len(password))
    score += diversity_count * 4.0
    # A 16-character password using all four character classes earns roughly
    # 80 points, while 20+ genuinely unpredictable characters can reach the
    # 90s. The cap is reachable without making entropy outweigh length.
    score += min(34.0, entropy / 3.2)
    has_patterns = any(
        bool(patterns[name])
        for name in (
            "is_common_password", "weak_words", "sequences", "repetitions", "years"
        )
    )
    unique_ratio = len(set(password.casefold())) / len(password) if password else 0.0
    if (
        len(password) >= 36
        and diversity_count == 4
        and entropy >= 200
        and unique_ratio >= 0.6
        and not has_patterns
    ):
        score += 2.0
    if patterns["is_common_password"]:
        score -= 55.0
    score -= min(24.0, len(patterns["weak_words"]) * 12.0)
    if patterns["sequences"]:
        score -= 12.0
    if patterns["repetitions"]:
        score -= 15.0
    if patterns["years"]:
        score -= 5.0
    return max(0, min(100, round(score)))
