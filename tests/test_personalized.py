"""Tests for deterministic personalized-predictability heuristics."""

from src.personalized import PersonalProfile, personalized_assessment


def profile(**updates: object) -> PersonalProfile:
    value: PersonalProfile = {
        "first_name": "",
        "last_name": "",
        "username": "",
        "birth_year": "",
        "keywords": [],
    }
    value.update(updates)  # type: ignore[typeddict-item]
    return value


def test_name_and_birth_year_are_detected_case_insensitively() -> None:
    result = personalized_assessment(
        "SARAH2004!", profile(first_name="Sarah", birth_year="2004")
    )
    personal = result["personal_predictability"]
    assert "first_name" in personal["matched_fields"]
    assert "birth_year" in personal["matched_fields"]
    assert personal["risk"] == "Critical"


def test_name_and_year_is_riskier_than_one_match() -> None:
    name_only = personalized_assessment("Sarah!Cobalt", profile(first_name="Sarah"))
    combined = personalized_assessment(
        "Sarah2004!", profile(first_name="Sarah", birth_year="2004")
    )
    assert (
        combined["personal_predictability"]["penalty"]
        > name_only["personal_predictability"]["penalty"]
    )


def test_username_fragment_is_detected_without_short_fragment_noise() -> None:
    result = personalized_assessment("Blue-Sarah-91!", profile(username="sarah.m"))
    assert "username" in result["personal_predictability"]["matched_fields"]
    unrelated = personalized_assessment("Mango-Moon-91!", profile(username="sarah.m"))
    assert "username" not in unrelated["personal_predictability"]["matched_fields"]


def test_short_birth_year_is_detected_with_a_personal_token() -> None:
    result = personalized_assessment(
        "Kader06", profile(first_name="Kader", birth_year="2006")
    )
    assert "birth_year" in result["personal_predictability"]["matched_fields"]


def test_birth_year_alone_has_moderate_risk() -> None:
    result = personalized_assessment("Orbit-2004-Cobalt", profile(birth_year="2004"))
    assert result["personal_predictability"]["risk"] == "Moderate"


def test_personal_keyword_and_year_combination_is_detected() -> None:
    result = personalized_assessment(
        "Football2026!", profile(keywords=["football"], birth_year="2026")
    )
    assert set(result["personal_predictability"]["matched_fields"]) == {
        "keywords", "birth_year"
    }


def test_no_profile_data_causes_no_penalty() -> None:
    result = personalized_assessment("G7!xP2#vQ9@Lm4$Zr8", profile())
    assert result["personal_predictability"]["risk"] == "Low"
    assert result["personal_predictability"]["penalty"] == 0
    assert result["personalized_score"] == result["technical"]["score"]


def test_unrelated_strong_password_has_low_personal_risk() -> None:
    result = personalized_assessment(
        "G7!xP2#vQ9@Lm4$Zr8", profile(first_name="Sarah", birth_year="2004")
    )
    assert result["personal_predictability"]["risk"] == "Low"


def test_personalized_score_never_exceeds_technical_score() -> None:
    result = personalized_assessment(
        "Sarah2004!", profile(first_name="Sarah", birth_year="2004")
    )
    assert 0 <= result["personalized_score"] <= result["technical"]["score"]


def test_result_does_not_contain_supplied_profile_values() -> None:
    result = personalized_assessment(
        "Sarah2004!", profile(first_name="SensitiveSentinel", username="private.handle")
    )
    rendered = str(result)
    assert "SensitiveSentinel" not in rendered
    assert "private.handle" not in rendered
