import pytest
from core.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    ConflictException,
    RateLimitException,
)


def test_app_exception_init():
    exc = AppException(status_code=400, detail="Test error")
    assert exc.status_code == 400
    assert exc.detail == "Test error"


def test_app_exception_with_headers():
    exc = AppException(
        status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"}
    )
    assert exc.headers == {"WWW-Authenticate": "Bearer"}


def test_not_found_exception():
    exc = NotFoundException("Resource not found")
    assert exc.status_code == 404
    assert exc.detail == "Resource not found"


def test_unauthorized_exception():
    exc = UnauthorizedException("Invalid credentials")
    assert exc.status_code == 401
    assert exc.detail == "Invalid credentials"


def test_forbidden_exception():
    exc = ForbiddenException("Access denied")
    assert exc.status_code == 403
    assert exc.detail == "Access denied"


def test_bad_request_exception():
    exc = BadRequestException("Invalid input")
    assert exc.status_code == 400
    assert exc.detail == "Invalid input"


def test_conflict_exception():
    exc = ConflictException("Resource already exists")
    assert exc.status_code == 409
    assert exc.detail == "Resource already exists"


def test_rate_limit_exception():
    exc = RateLimitException("Too many requests")
    assert exc.status_code == 429
    assert exc.detail == "Too many requests"


def test_exception_inheritance():
    exc = NotFoundException("test")
    assert isinstance(exc, AppException)
