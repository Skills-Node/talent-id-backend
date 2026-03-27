import pytest
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    decode_token,
)


def test_get_password_hash():
    hash1 = get_password_hash("test_password")
    hash2 = get_password_hash("test_password")

    assert hash1 is not None
    assert len(hash1) > 0
    assert hash1 != "test_password"


def test_verify_password_success():
    password = "test_password"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    password = "test_password"
    wrong_password = "wrong_password"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False


def test_create_access_token():
    token = create_access_token(data={"sub": "test-user-id"})

    assert token is not None
    assert len(token) > 0
    assert isinstance(token, str)


def test_create_refresh_token():
    token = create_refresh_token(data={"sub": "test-user-id"})

    assert token is not None
    assert len(token) > 0
    assert isinstance(token, str)


def test_decode_token_valid_access():
    token = create_access_token(data={"sub": "test-user-id"})

    payload = decode_token(token)

    assert payload is not None
    assert payload.get("sub") == "test-user-id"


def test_decode_token_valid_refresh():
    token = create_refresh_token(data={"sub": "test-user-id"})

    payload = decode_token(token)

    assert payload is not None
    assert payload.get("sub") == "test-user-id"


def test_decode_token_invalid():
    with pytest.raises(Exception):
        decode_token("invalid_token")


def test_access_token_has_type_claim():
    token = create_access_token(data={"sub": "test-user-id"})
    payload = decode_token(token)

    assert payload.get("type") == "access"


def test_refresh_token_has_type_claim():
    token = create_refresh_token(data={"sub": "test-user-id"})
    payload = decode_token(token)

    assert payload.get("type") == "refresh"


def test_verify_refresh_token_valid():
    token = create_refresh_token(data={"sub": "test-user-id", "exp": 9999999999})

    payload = verify_refresh_token(token)

    assert payload is not None
    assert payload.get("sub") == "test-user-id"


def test_verify_refresh_token_invalid():
    with pytest.raises(Exception):
        verify_refresh_token("invalid.token.here")
