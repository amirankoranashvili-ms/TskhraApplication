"""Unit tests for CSRF helper functions."""

from unittest.mock import MagicMock

from src.app.infra.web.controllers.verification_controller import (
    _set_csrf_token,
    _validate_csrf,
)


class TestSetCsrfToken:
    def test_generates_and_stores_token(self):
        request = MagicMock()
        request.session = {}

        token = _set_csrf_token(request)

        assert len(token) == 64  # 32 bytes -> 64 hex chars
        assert request.session["csrf_token"] == token

    def test_generates_unique_tokens(self):
        request = MagicMock()
        request.session = {}

        token1 = _set_csrf_token(request)
        token2 = _set_csrf_token(request)

        assert token1 != token2


class TestValidateCsrf:
    def test_valid_token(self):
        request = MagicMock()
        request.session = {"csrf_token": "abc123"}

        assert _validate_csrf(request, {"csrf_token": "abc123"}) is True

    def test_invalid_token(self):
        request = MagicMock()
        request.session = {"csrf_token": "abc123"}

        assert _validate_csrf(request, {"csrf_token": "wrong"}) is False

    def test_missing_form_token(self):
        request = MagicMock()
        request.session = {"csrf_token": "abc123"}

        assert _validate_csrf(request, {}) is False

    def test_empty_form_token(self):
        request = MagicMock()
        request.session = {"csrf_token": "abc123"}

        assert _validate_csrf(request, {"csrf_token": ""}) is False

    def test_missing_session_token(self):
        request = MagicMock()
        request.session = {}

        assert _validate_csrf(request, {"csrf_token": "abc123"}) is False
