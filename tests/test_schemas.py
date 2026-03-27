import pytest
from pydantic import ValidationError
from schemas import (
    UserCreate,
    UserLogin,
    ProfileRequestInput,
    Competency,
    MatchingRequestInput,
)


def test_user_create_valid():
    user = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User",
    )
    assert user.email == "test@example.com"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="invalid-email",
            password="password123",
            full_name="Test User",
        )


def test_user_create_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="short",
            full_name="Test User",
        )


def test_profile_request_input_valid():
    request = ProfileRequestInput(
        name="John Smith",
        date_of_birth="1990-01-15",
        enneagram_answers="1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
    )
    assert request.name == "John Smith"
    assert request.date_of_birth == "1990-01-15"


def test_profile_request_input_empty_name():
    with pytest.raises(ValidationError):
        ProfileRequestInput(
            name="",
            date_of_birth="1990-01-15",
            enneagram_answers="1,2,3,4,5",
        )


def test_competency_valid():
    comp = Competency(name="Leadership", value=85)
    assert comp.name == "Leadership"
    assert comp.value == 85


def test_competency_invalid_value():
    with pytest.raises(ValidationError):
        Competency(name="Leadership", value=150)


def test_competency_negative_value():
    with pytest.raises(ValidationError):
        Competency(name="Leadership", value=-10)


def test_matching_request_input_valid():
    request = MatchingRequestInput(
        profile_id="profile-123",
        leader_data="Looking for a strategic technical partner",
    )
    assert request.profile_id == "profile-123"
    assert request.leader_data == "Looking for a strategic technical partner"


def test_matching_request_input_empty_leader_data():
    with pytest.raises(ValidationError):
        MatchingRequestInput(
            profile_id="profile-123",
            leader_data="",
        )


def test_profile_request_input_missing_fields():
    with pytest.raises(ValidationError):
        ProfileRequestInput(
            name="Test",
            # missing date_of_birth and enneagram_answers
        )


def test_matching_request_input_missing_profile_id():
    with pytest.raises(ValidationError):
        MatchingRequestInput(
            leader_data="Some data",
        )
