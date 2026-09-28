import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    raw = "scientific_secure_pw_2026"
    hashed = get_password_hash(raw)
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_lifecycle():
    token = create_access_token({"sub": "42", "role": "RESEARCHER", "username": "dr_curie"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "42"
    assert payload.get("role") == "RESEARCHER"
    assert payload.get("username") == "dr_curie"


def test_invalid_jwt_token():
    invalid_token = "invalid.token.payload"
    assert decode_access_token(invalid_token) is None
