import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from services.auth_service import AuthService
from schemas import (
    UserCreate,
    UserUpdate,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
)
from core import NotFoundException, UnauthorizedException


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_token_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_hash = AsyncMock()
    repo.revoke = AsyncMock()
    repo.revoke_all_for_user = AsyncMock()
    return repo


@pytest.fixture
def auth_service(mock_db, mock_user_repo, mock_token_repo):
    service = AuthService(mock_db)
    service.user_repo = mock_user_repo
    service.token_repo = mock_token_repo
    return service


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.hashed_password = "hashed_password"
    user.is_active = True
    user.full_name = "Test User"
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_user_repo):
    user_data = UserCreate(
        email="new@example.com", password="password123", full_name="New User"
    )

    mock_user_repo.get_by_email.return_value = None

    with patch(
        "services.auth_service.AuthService.login", new_callable=AsyncMock
    ) as mock_login:
        mock_login.return_value = TokenResponse(
            access_token="access_token", refresh_token="refresh_token"
        )
        result = await auth_service.register(user_data)

    mock_user_repo.create.assert_called_once()
    assert result.access_token == "access_token"


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_user_repo, mock_token_repo, mock_user):
    credentials = UserLogin(email="test@example.com", password="password123")
    mock_user_repo.get_by_email.return_value = mock_user

    with (
        patch("services.auth_service.create_access_token") as mock_create_access,
        patch("services.auth_service.create_refresh_token") as mock_create_refresh,
        patch("services.auth_service.get_password_hash") as mock_hash,
        patch("services.auth_service.verify_password", return_value=True),
    ):
        mock_create_access.return_value = "access_jwt"
        mock_create_refresh.return_value = "refresh_jwt"
        mock_hash.return_value = "token_hash"

        result = await auth_service.login(credentials)

    assert result.access_token == "access_jwt"
    assert "." in result.refresh_token


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_user_repo):
    credentials = UserLogin(email="notfound@example.com", password="password123")
    mock_user_repo.get_by_email.return_value = None

    with pytest.raises(UnauthorizedException) as exc:
        await auth_service.login(credentials)

    assert "Invalid email or password" in str(exc.value)


@pytest.mark.asyncio
async def test_login_wrong_password(auth_service, mock_user_repo, mock_user):
    credentials = UserLogin(email="test@example.com", password="wrongpassword")
    mock_user_repo.get_by_email.return_value = mock_user

    with patch("services.auth_service.verify_password", return_value=False):
        with pytest.raises(UnauthorizedException) as exc:
            await auth_service.login(credentials)

    assert "Invalid email or password" in str(exc.value)


@pytest.mark.asyncio
async def test_login_inactive_user(auth_service, mock_user_repo, mock_user):
    mock_user.is_active = False
    credentials = UserLogin(email="test@example.com", password="password123")
    mock_user_repo.get_by_email.return_value = mock_user

    with patch("services.auth_service.verify_password", return_value=True):
        with pytest.raises(UnauthorizedException) as exc:
            await auth_service.login(credentials)

    assert "inactive" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_refresh_tokens_success(
    auth_service, mock_user_repo, mock_token_repo, mock_user
):
    refresh_request = RefreshTokenRequest(
        refresh_token="token_id.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQifQ"
    )

    mock_user_repo.get_by_id.return_value = mock_user
    mock_token_repo.get_by_token_id.return_value = MagicMock(
        token_id="token_id", revoked=False
    )

    with (
        patch("services.auth_service.verify_refresh_token") as mock_verify,
        patch("services.auth_service.create_access_token") as mock_create_access,
        patch("services.auth_service.create_refresh_token") as mock_create_refresh,
    ):
        mock_verify.return_value = {
            "sub": "test-user-id",
            "exp": 9999999999,
            "type": "refresh",
        }
        mock_create_access.return_value = "new_access"
        mock_create_refresh.return_value = "new_refresh"

        result = await auth_service.refresh_tokens(refresh_request)

    assert result.access_token == "new_access"


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_format(auth_service):
    refresh_request = RefreshTokenRequest(refresh_token="invalid_format")

    with pytest.raises(UnauthorizedException) as exc:
        await auth_service.refresh_tokens(refresh_request)

    assert "Invalid refresh token format" in str(exc.value)


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_token(auth_service):
    refresh_request = RefreshTokenRequest(refresh_token="token_id.invalid.jwt")

    with patch(
        "services.auth_service.verify_refresh_token", side_effect=Exception("Invalid")
    ):
        with pytest.raises(UnauthorizedException) as exc:
            await auth_service.refresh_tokens(refresh_request)

    assert "Invalid refresh token" in str(exc.value)


@pytest.mark.asyncio
async def test_refresh_tokens_user_not_found(auth_service, mock_user_repo):
    refresh_request = RefreshTokenRequest(
        refresh_token="token_id.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJub25leGlzdGVkIn0.signature"
    )

    mock_user_repo.get_by_id.return_value = None

    with patch("services.auth_service.verify_refresh_token") as mock_verify:
        mock_verify.return_value = {"sub": "nonexistent-user", "exp": 9999999999}

        with pytest.raises(UnauthorizedException) as exc:
            await auth_service.refresh_tokens(refresh_request)

        assert "Invalid refresh token" in str(exc.value)


@pytest.mark.asyncio
async def test_refresh_tokens_token_id_mismatch(
    auth_service, mock_user_repo, mock_token_repo, mock_user
):
    refresh_request = RefreshTokenRequest(
        refresh_token="token_id.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQifQ"
    )

    mock_user_repo.get_by_id.return_value = mock_user
    mock_token_repo.get_by_token_id.return_value = MagicMock(
        token_id="different_token_id", revoked=False
    )

    with (
        patch("services.auth_service.verify_refresh_token") as mock_verify,
    ):
        mock_verify.return_value = {
            "sub": "test-user-id",
            "exp": 9999999999,
            "type": "refresh",
        }

        with pytest.raises(UnauthorizedException) as exc:
            await auth_service.refresh_tokens(refresh_request)

    assert "Invalid refresh token" in str(exc.value)


@pytest.mark.asyncio
async def test_get_user_by_id_success(auth_service, mock_user_repo, mock_user):
    mock_user_repo.get_by_id.return_value = mock_user

    result = await auth_service.get_user_by_id("test-user-id")

    assert result.email == "test@example.com"
    assert result.full_name == "Test User"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(auth_service, mock_user_repo):
    mock_user_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException) as exc:
        await auth_service.get_user_by_id("nonexistent-id")

    assert "User not found" in str(exc.value)


@pytest.mark.asyncio
async def test_update_user_success(auth_service, mock_user_repo, mock_user):
    user_data = UserUpdate(full_name="Updated Name")
    mock_user_repo.update.return_value = mock_user
    mock_user.full_name = "Updated Name"

    result = await auth_service.update_user("test-user-id", user_data)

    mock_user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_with_password(auth_service, mock_user_repo, mock_user):
    user_data = UserUpdate(password="newpassword123", full_name="Updated Name")
    mock_user_repo.update.return_value = mock_user

    result = await auth_service.update_user("test-user-id", user_data)

    call_kwargs = mock_user_repo.update.call_args[1]
    assert "password" in call_kwargs


@pytest.mark.asyncio
async def test_logout_success(auth_service, mock_token_repo):
    await auth_service.logout("test-user-id")

    mock_token_repo.revoke_all_for_user.assert_called_once_with("test-user-id")
