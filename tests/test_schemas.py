import pytest
from pydantic import ValidationError
from schemas import (
    UserCreate,
    UserLogin,
    PerfilRequestInput,
    Competencia,
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


def test_perfil_request_input_valid():
    request = PerfilRequestInput(
        nombre="Juan Pérez",
        fecha_nacimiento="1990-01-15",
        respuestas_eneagrama="123321123",
    )
    assert request.nombre == "Juan Pérez"


def test_perfil_request_input_empty_nombre():
    with pytest.raises(ValidationError):
        PerfilRequestInput(
            nombre="",
            fecha_nacimiento="1990-01-15",
            respuestas_eneagrama="123321123",
        )


def test_competencia_valid():
    comp = Competencia(nombre="Liderazgo", valor=85)
    assert comp.nombre == "Liderazgo"
    assert comp.valor == 85


def test_competencia_invalid_value():
    with pytest.raises(ValidationError):
        Competencia(nombre="Liderazgo", valor=150)


def test_competencia_negative_value():
    with pytest.raises(ValidationError):
        Competencia(nombre="Liderazgo", valor=-10)


def test_matching_request_input_valid():
    request = MatchingRequestInput(
        profile_id="profile-123",
        datos_lider="Líder tipo A con experiencia",
    )
    assert request.profile_id == "profile-123"


def test_matching_request_input_empty_datos():
    with pytest.raises(ValidationError):
        MatchingRequestInput(
            profile_id="profile-123",
            datos_lider="",
        )
