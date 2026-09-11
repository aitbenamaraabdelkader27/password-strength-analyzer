"""API integration, validation, and privacy tests for V2 endpoints."""

import string

import pytest

from app import create_app
from src.analyzer import analyze_password


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-only"})
    return app.test_client()


def test_personalized_api_separates_technical_and_personal_results(client) -> None:
    response = client.post(
        "/api/analyze/personalized",
        json={
            "password": "Sarah2004!",
            "profile": {"first_name": "Sarah", "birth_year": "2004"},
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["technical"]["score"] >= data["personalized_score"]
    assert data["personal_predictability"]["risk"] == "Critical"
    assert b"Sarah2004!" not in response.data


def test_personalized_api_accepts_an_empty_profile(client) -> None:
    response = client.post(
        "/api/analyze/personalized",
        json={"password": "G7!xP2#vQ9@Lm4$Z", "profile": {}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["personalized_score"] == data["technical"]["score"]


@pytest.mark.parametrize(
    "profile",
    [
        [],
        {"first_name": 42},
        {"birth_year": "04"},
        {"birth_year": "2200"},
        {"keywords": "not-a-list"},
        {"keywords": ["a", "b", "c", "d", "e", "f"]},
        {"keywords": [17]},
    ],
)
def test_personalized_api_rejects_malformed_profiles(client, profile) -> None:
    response = client.post(
        "/api/analyze/personalized",
        json={"password": "Fake-Test-Password!7", "profile": profile},
    )
    assert response.status_code == 400


def test_personal_values_are_not_reflected_in_validation_errors(client) -> None:
    sensitive_marker = "PrivateProfileMarker"
    response = client.post(
        "/api/analyze/personalized",
        json={
            "password": "Fake-Test-Password!7",
            "profile": {"first_name": sensitive_marker, "birth_year": "invalid"},
        },
    )
    assert response.status_code == 400
    assert sensitive_marker.encode() not in response.data


def test_personalized_api_rejects_oversized_fields(client) -> None:
    response = client.post(
        "/api/analyze/personalized",
        json={
            "password": "Fake-Test-Password!7",
            "profile": {"username": "x" * 65},
        },
    )
    assert response.status_code == 413


def test_malformed_json_is_rejected_without_internal_error(client) -> None:
    for endpoint in (
        "/api/analyze",
        "/api/analyze/personalized",
        "/api/generate/random",
        "/api/generate/passphrase",
    ):
        response = client.post(
            endpoint, data="{broken", content_type="application/json"
        )
        assert response.status_code == 400


def test_oversized_request_body_is_rejected(client) -> None:
    response = client.post(
        "/api/analyze",
        data='{"password":"' + ("x" * 5000) + '"}',
        content_type="application/json",
    )
    assert response.status_code == 413


def test_random_generator_api_returns_requested_password_and_same_analysis(client) -> None:
    response = client.post(
        "/api/generate/random",
        json={
            "length": 24,
            "uppercase": False,
            "lowercase": True,
            "digits": False,
            "symbols": False,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["password"]) == 24
    assert set(data["password"]) <= set(string.ascii_lowercase)
    assert data["analysis"] == analyze_password(data["password"])


def test_random_generator_api_rejects_no_character_sets(client) -> None:
    response = client.post(
        "/api/generate/random",
        json={
            "uppercase": False,
            "lowercase": False,
            "digits": False,
            "symbols": False,
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize("length", [11, 65, "20", True])
def test_random_generator_api_validates_length(client, length) -> None:
    assert client.post("/api/generate/random", json={"length": length}).status_code == 400


def test_passphrase_api_respects_options_and_uses_main_analyzer(client) -> None:
    response = client.post(
        "/api/generate/passphrase",
        json={
            "word_count": 4,
            "separator": ".",
            "capitalize": False,
            "include_number": False,
            "include_symbol": False,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["password"].split(".")) == 4
    assert data["word_pool_size"] == 256
    assert data["analysis"] == analyze_password(data["password"])


@pytest.mark.parametrize(
    "payload",
    [
        {"word_count": 2},
        {"word_count": 7},
        {"word_count": True},
        {"separator": "/"},
        {"capitalize": "yes"},
    ],
)
def test_passphrase_api_rejects_invalid_options(client, payload) -> None:
    assert client.post("/api/generate/passphrase", json=payload).status_code == 400


def test_v2_api_responses_disable_caching(client) -> None:
    response = client.post("/api/generate/random", json={})
    assert response.headers["Cache-Control"].startswith("no-store")
