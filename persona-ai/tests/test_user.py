"""User security and token unit tests."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.security import (
    create_access_token,
    hash_password,
    parse_user_id_from_token,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    h = hash_password("correct-horse-battery")
    assert verify_password("correct-horse-battery", h)
    assert not verify_password("wrong", h)


def test_password_rejects_over_72_bytes() -> None:
    long_pw = "x" * 100
    with pytest.raises(ValueError):
        hash_password(long_pw)


def test_jwt_roundtrip() -> None:
    uid = uuid4()
    token = create_access_token(subject=uid)
    assert parse_user_id_from_token(token) == uid
