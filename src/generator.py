"""Cryptographically secure password and passphrase generation."""

from __future__ import annotations

import math
import secrets
import string
from typing import TypedDict

from .words import WORDS

SYMBOLS = "!@#$%&*?"
PASSPHRASE_SEPARATORS = ("-", "_", ".", " ")


class GeneratedSecret(TypedDict):
    """Generated value and transparent generation metadata."""

    password: str
    selection_entropy: float


def generate_random_password(
    length: int = 20,
    *,
    uppercase: bool = True,
    lowercase: bool = True,
    digits: bool = True,
    symbols: bool = True,
) -> GeneratedSecret:
    """Generate a password while guaranteeing every enabled set is represented."""
    if not 12 <= length <= 64:
        raise ValueError("Length must be between 12 and 64.")
    sets = []
    if uppercase:
        sets.append(string.ascii_uppercase)
    if lowercase:
        sets.append(string.ascii_lowercase)
    if digits:
        sets.append(string.digits)
    if symbols:
        sets.append(SYMBOLS)
    if not sets:
        raise ValueError("Select at least one character set.")
    if length < len(sets):
        raise ValueError("Length is too short for the selected character sets.")

    alphabet = "".join(sets)
    characters = [secrets.choice(character_set) for character_set in sets]
    characters.extend(secrets.choice(alphabet) for _ in range(length - len(sets)))
    secrets.SystemRandom().shuffle(characters)
    return {
        "password": "".join(characters),
        "selection_entropy": round(length * math.log2(len(alphabet)), 1),
    }


def generate_passphrase(
    word_count: int = 5,
    *,
    separator: str = "-",
    capitalize: bool = True,
    include_number: bool = True,
    include_symbol: bool = True,
) -> GeneratedSecret:
    """Generate independently selected, unrelated words with optional additions."""
    if not 3 <= word_count <= 6:
        raise ValueError("Word count must be between 3 and 6.")
    if separator not in PASSPHRASE_SEPARATORS:
        raise ValueError("Choose an allowed separator.")
    selected = [secrets.choice(WORDS) for _ in range(word_count)]
    if capitalize:
        selected = [word.capitalize() for word in selected]
    phrase = separator.join(selected)
    entropy = word_count * math.log2(len(WORDS))
    if include_number:
        phrase += f"{separator}{secrets.randbelow(90) + 10}"
        entropy += math.log2(90)
    if include_symbol:
        phrase += secrets.choice(SYMBOLS)
        entropy += math.log2(len(SYMBOLS))
    return {"password": phrase, "selection_entropy": round(entropy, 1)}
