import pytest
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    verify_refresh_token,
)


def test_password_hash_and_verify():
    password = "test_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_create_and_decode_access_token():
    token = create_access_token(data={"sub": "user-123"})

    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_and_verify_refresh_token():
    from core.security import create_refresh_token

    token = create_refresh_token(data={"sub": "user-456"}, expires_delta=None)

    payload = verify_refresh_token(token)

    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"


def test_verify_refresh_token_rejects_access_token():
    access_token = create_access_token(data={"sub": "user-789"}, expires_delta=None)

    with pytest.raises(Exception):
        verify_refresh_token(access_token)
