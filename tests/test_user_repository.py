import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from repositories.user_repository import UserRepository
from core.database import Base


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def user_repo(mock_db):
    return UserRepository(mock_db)


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.hashed_password = "hashed_password"
    user.full_name = "Test User"
    user.is_active = True
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    return user


@pytest.mark.asyncio
async def test_get_by_email(user_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await user_repo.get_by_email("test@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_email_found(user_repo, mock_db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    result = await user_repo.get_by_email("test@example.com")

    assert result is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_by_id(user_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await user_repo.get_by_id("test-id")

    assert result is None


@pytest.mark.asyncio
async def test_create(user_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    await user_repo.create(
        email="new@example.com", password="password123", full_name="New User"
    )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_duplicate_email(user_repo, mock_db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    with pytest.raises(Exception):
        await user_repo.create(
            email="existing@example.com", password="password123", full_name="New User"
        )


@pytest.mark.asyncio
async def test_update(user_repo, mock_db):
    mock_existing = MagicMock()
    mock_existing.email = "old@example.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_existing
    mock_db.execute.return_value = mock_result

    await user_repo.update("test-id", email="new@example.com")

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_password(user_repo, mock_db):
    mock_existing = MagicMock()
    mock_existing.email = "old@example.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_existing
    mock_db.execute.return_value = mock_result

    await user_repo.update("test-id", password="newpassword123")

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(user_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(Exception):
        await user_repo.update("nonexistent-id", email="new@example.com")


@pytest.mark.asyncio
async def test_delete(user_repo, mock_db):
    mock_existing = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_existing
    mock_db.execute.return_value = mock_result

    await user_repo.delete("test-id")

    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(user_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(Exception):
        await user_repo.delete("nonexistent-id")
