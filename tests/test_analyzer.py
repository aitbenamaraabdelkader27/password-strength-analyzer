"""Integration tests for analysis results and the Flask API."""

import pytest

from app import MAX_PASSWORD_LENGTH, create_app
from src.analyzer import analyze_password


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-only"})
    return app.test_client()


@pytest.mark.parametrize("password", ["123456", "password", "qwerty"])
def test_known_weak_passwords_are_very_weak(password: str) -> None:
    result = analyze_password(password)
    assert result["strength"] == "Very Weak"
    assert result["patterns"]["common_password"] is True


def test_medium_password() -> None:
    assert analyze_password("Cobalt7!")["strength"] == "Medium"


def test_strong_password() -> None:
    assert analyze_password("M7!vQ2#kL9@xR4$p")["strength"] in {
        "Strong", "Very Strong"
    }


def test_very_long_passphrase_gets_length_credit() -> None:
    result = analyze_password("violet-harbor-lantern-cosmos")
    assert result["checks"]["length_20"] is True
    assert result["score"] >= 60


def test_repetition_creates_issue_and_recommendation() -> None:
    result = analyze_password("Ababababab9!")
    assert result["patterns"]["repetition"] is True
    assert any("Repeated" in issue for issue in result["issues"])
    assert any("repeated" in item for item in result["recommendations"])


def test_result_never_contains_password() -> None:
    submitted = "Unique-Sentinel-Value!9"
    result = analyze_password(submitted)
    assert "password" not in result
    assert submitted not in str(result)


def test_api_returns_analysis_without_echoing_password(client) -> None:
    submitted = "Ocean!Maple7-Circuit"
    response = client.post("/api/analyze", json={"password": submitted})
    assert response.status_code == 200
    assert submitted.encode() not in response.data
    assert response.headers["Cache-Control"].startswith("no-store")
    assert "Content-Security-Policy" in response.headers


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        ({}, 400),
        ({"password": None}, 400),
        ({"password": 1234}, 400),
        ({"password": ""}, 400),
    ],
)
def test_api_rejects_invalid_passwords(client, payload, status: int) -> None:
    assert client.post("/api/analyze", json=payload).status_code == status


def test_api_requires_json(client) -> None:
    assert client.post("/api/analyze", data="password=secret").status_code == 415


def test_api_rejects_excessively_long_password(client) -> None:
    response = client.post(
        "/api/analyze", json={"password": "x" * (MAX_PASSWORD_LENGTH + 1)}
    )
    assert response.status_code == 413


def test_index_loads_privacy_message(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Your password is analyzed securely and is never stored." in response.data
