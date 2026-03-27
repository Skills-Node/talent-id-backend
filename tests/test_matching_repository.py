import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from repositories.matching_repository import MatchingRepository


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
def matching_repo(mock_db):
    return MatchingRepository(mock_db)


@pytest.fixture
def mock_matching():
    matching = MagicMock()
    matching.id = "test-matching-id"
    matching.profile_id = "test-profile-id"
    matching.leader_data = "Test leader data"
    matching.leader_personality_type = None
    matching.match_percentage = None
    matching.strengths = None
    matching.conflict_zones = None
    matching.created_at = datetime.now(timezone.utc)
    return matching


@pytest.mark.asyncio
async def test_get_by_id(matching_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await matching_repo.get_by_id("test-id")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_found(matching_repo, mock_db, mock_matching):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_matching
    mock_db.execute.return_value = mock_result

    result = await matching_repo.get_by_id("test-id")

    assert result is not None
    assert result.id == "test-matching-id"


@pytest.mark.asyncio
async def test_get_by_profile_id(matching_repo, mock_db, mock_matching):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_matching]
    mock_db.execute.return_value = mock_result

    result = await matching_repo.get_by_profile_id("test-profile-id")

    assert len(result) == 1
    assert result[0].id == "test-matching-id"


@pytest.mark.asyncio
async def test_get_by_profile_id_empty(matching_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await matching_repo.get_by_profile_id("test-profile-id")

    assert result == []


@pytest.mark.asyncio
async def test_create(matching_repo, mock_db):
    await matching_repo.create(profile_id="test-profile-id", leader_data="Test data")

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete(matching_repo, mock_db, mock_matching):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_matching
    mock_db.execute.return_value = mock_result

    await matching_repo.delete("test-matching-id")

    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(matching_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(Exception):
        await matching_repo.delete("nonexistent-id")


@pytest.mark.asyncio
async def test_count_by_profile(matching_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 5
    mock_db.execute.return_value = mock_result

    result = await matching_repo.count_by_profile("test-profile-id")

    assert result == 5


@pytest.mark.asyncio
async def test_count_by_profile_zero(matching_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar.return_value = None
    mock_db.execute.return_value = mock_result

    result = await matching_repo.count_by_profile("test-profile-id")

    assert result == 0
