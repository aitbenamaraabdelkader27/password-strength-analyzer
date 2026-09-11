"""Flask entry point for the Password Strength Analyzer."""

from __future__ import annotations

import os
import re
from typing import Any

from flask import Flask, jsonify, render_template, request

from src.analyzer import analyze_password
from src.generator import (
    PASSPHRASE_SEPARATORS,
    generate_passphrase,
    generate_random_password,
)
from src.personalized import PersonalProfile, personalized_assessment

MAX_PASSWORD_LENGTH = 256
MAX_PERSONAL_FIELD_LENGTH = 64
MAX_KEYWORD_LENGTH = 32
MAX_PERSONAL_KEYWORDS = 5
RANDOM_LENGTH_RANGE = range(12, 65)
PASSPHRASE_WORD_RANGE = range(3, 7)
BIRTH_YEAR_RE = re.compile(r"(?:19|20)\d{2}")


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=4 * 1024,
        SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(32),
    )
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index() -> str:
        return render_template("index.html", max_password_length=MAX_PASSWORD_LENGTH)

    @app.post("/api/analyze")
    def analyze() -> tuple[Any, int] | Any:
        payload, error = _json_object()
        if error:
            return error
        password, error = _validated_password(payload)
        if error:
            return error
        return jsonify(analyze_password(password))

    @app.post("/api/analyze/personalized")
    def analyze_personalized() -> tuple[Any, int] | Any:
        payload, error = _json_object()
        if error:
            return error
        password, error = _validated_password(payload)
        if error:
            return error
        profile, error = _validated_profile(payload.get("profile", {}))
        if error:
            return error
        return jsonify(personalized_assessment(password, profile))

    @app.post("/api/generate/random")
    def generate_random() -> tuple[Any, int] | Any:
        payload, error = _json_object()
        if error:
            return error
        length = payload.get("length", 20)
        if isinstance(length, bool) or not isinstance(length, int):
            return jsonify(error="Length must be an integer."), 400
        if length not in RANDOM_LENGTH_RANGE:
            return jsonify(error="Length must be between 12 and 64."), 400

        option_names = ("uppercase", "lowercase", "digits", "symbols")
        options: dict[str, bool] = {}
        for name in option_names:
            value = payload.get(name, True)
            if not isinstance(value, bool):
                return jsonify(error=f"{name.capitalize()} must be true or false."), 400
            options[name] = value
        try:
            generated = generate_random_password(length, **options)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(_generated_response(generated))

    @app.post("/api/generate/passphrase")
    def generate_memorable() -> tuple[Any, int] | Any:
        payload, error = _json_object()
        if error:
            return error
        word_count = payload.get("word_count", 5)
        if isinstance(word_count, bool) or not isinstance(word_count, int):
            return jsonify(error="Word count must be an integer."), 400
        if word_count not in PASSPHRASE_WORD_RANGE:
            return jsonify(error="Word count must be between 3 and 6."), 400
        separator = payload.get("separator", "-")
        if separator not in PASSPHRASE_SEPARATORS:
            return jsonify(error="Choose an allowed separator."), 400

        flags: dict[str, bool] = {}
        for name in ("capitalize", "include_number", "include_symbol"):
            value = payload.get(name, True)
            if not isinstance(value, bool):
                return jsonify(error=f"{name.capitalize()} must be true or false."), 400
            flags[name] = value
        generated = generate_passphrase(word_count, separator=separator, **flags)
        response = _generated_response(generated)
        response["word_count"] = word_count
        response["word_pool_size"] = 256
        return jsonify(response)

    @app.errorhandler(413)
    def request_too_large(_error: Exception) -> tuple[Any, int]:
        return jsonify(error="Request body is too large."), 413

    @app.errorhandler(500)
    def internal_error(_error: Exception) -> tuple[Any, int]:
        return jsonify(error="An unexpected error occurred."), 500

    @app.after_request
    def set_security_headers(response: Any) -> Any:
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return app


def _json_object() -> tuple[dict[str, Any], None] | tuple[dict[str, Any], tuple[Any, int]]:
    """Read a JSON object without reflecting any submitted values."""
    if not request.is_json:
        return {}, (jsonify(error="Request body must be JSON."), 415)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {}, (jsonify(error="Request body must be a JSON object."), 400)
    return payload, None


def _validated_password(
    payload: dict[str, Any],
) -> tuple[str, None] | tuple[str, tuple[Any, int]]:
    password = payload.get("password")
    if password is None:
        return "", (jsonify(error="The password field is required."), 400)
    if not isinstance(password, str):
        return "", (jsonify(error="Password must be a string."), 400)
    if not password:
        return "", (jsonify(error="Password cannot be empty."), 400)
    if len(password) > MAX_PASSWORD_LENGTH:
        return "", (
            jsonify(error=f"Password must be {MAX_PASSWORD_LENGTH} characters or fewer."),
            413,
        )
    return password, None


def _validated_profile(
    value: Any,
) -> tuple[PersonalProfile, None] | tuple[PersonalProfile, tuple[Any, int]]:
    empty: PersonalProfile = {
        "first_name": "", "last_name": "", "username": "",
        "birth_year": "", "keywords": [],
    }
    if not isinstance(value, dict):
        return empty, (jsonify(error="Profile must be a JSON object."), 400)
    profile = empty.copy()
    for name in ("first_name", "last_name", "username"):
        field = value.get(name, "")
        if not isinstance(field, str):
            return empty, (jsonify(error=f"{name.capitalize()} must be a string."), 400)
        if len(field) > MAX_PERSONAL_FIELD_LENGTH:
            return empty, (jsonify(error=f"{name.capitalize()} is too long."), 413)
        profile[name] = field.strip()

    birth_year = value.get("birth_year", "")
    if isinstance(birth_year, int) and not isinstance(birth_year, bool):
        birth_year = str(birth_year)
    if not isinstance(birth_year, str):
        return empty, (jsonify(error="Birth year must be a four-digit year."), 400)
    birth_year = birth_year.strip()
    if birth_year and not BIRTH_YEAR_RE.fullmatch(birth_year):
        return empty, (jsonify(error="Birth year must be between 1900 and 2099."), 400)
    profile["birth_year"] = birth_year

    keywords = value.get("keywords", [])
    if not isinstance(keywords, list) or len(keywords) > MAX_PERSONAL_KEYWORDS:
        return empty, (jsonify(error="Provide no more than 5 personal keywords."), 400)
    clean_keywords = []
    for keyword in keywords:
        if not isinstance(keyword, str):
            return empty, (jsonify(error="Each personal keyword must be a string."), 400)
        clean = keyword.strip()
        if len(clean) > MAX_KEYWORD_LENGTH:
            return empty, (
                jsonify(error="Each personal keyword must be 32 characters or fewer."),
                413,
            )
        if clean:
            clean_keywords.append(clean)
    profile["keywords"] = clean_keywords
    return profile, None


def _generated_response(generated: dict[str, Any]) -> dict[str, Any]:
    password = generated["password"]
    return {
        "password": password,
        "selection_entropy": generated["selection_entropy"],
        "analysis": analyze_password(password),
    }


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
