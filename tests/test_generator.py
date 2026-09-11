"""Tests for cryptographically secure password generation."""

import inspect
import re
import string

import pytest

import src.generator as generator
from src.generator import SYMBOLS, generate_passphrase, generate_random_password
from src.words import WORDS


def test_word_pool_is_unique_power_of_two() -> None:
    assert len(WORDS) == 256
    assert len(set(WORDS)) == len(WORDS)


def test_random_password_respects_length_and_enabled_set() -> None:
    result = generate_random_password(
        32, uppercase=False, lowercase=False, digits=True, symbols=False
    )
    assert len(result["password"]) == 32
    assert set(result["password"]) <= set(string.digits)


def test_random_password_contains_each_enabled_character_type() -> None:
    password = generate_random_password(20)["password"]
    assert any(character.isupper() for character in password)
    assert any(character.islower() for character in password)
    assert any(character.isdigit() for character in password)
    assert any(character in SYMBOLS for character in password)


def test_random_passwords_vary() -> None:
    assert generate_random_password()["password"] != generate_random_password()["password"]


def test_random_generator_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        generate_random_password(11)
    with pytest.raises(ValueError):
        generate_random_password(
            20, uppercase=False, lowercase=False, digits=False, symbols=False
        )


def test_generator_uses_secrets_not_standard_random_module() -> None:
    source = inspect.getsource(generator)
    assert "import secrets" in source
    assert "import random" not in source
    assert "Math.random" not in source


def test_passphrase_word_count_and_separator() -> None:
    password = generate_passphrase(
        4, separator="_", capitalize=False,
        include_number=False, include_symbol=False,
    )["password"]
    parts = password.split("_")
    assert len(parts) == 4
    assert all(part in WORDS for part in parts)


def test_passphrase_optional_number_and_symbol() -> None:
    password = generate_passphrase(3, separator="-")["password"]
    assert re.search(r"-\d{2}[!@#$%&*?]$", password)


def test_passphrases_vary() -> None:
    assert generate_passphrase()["password"] != generate_passphrase()["password"]


def test_passphrase_rejects_invalid_options() -> None:
    with pytest.raises(ValueError):
        generate_passphrase(2)
    with pytest.raises(ValueError):
        generate_passphrase(4, separator="/")
