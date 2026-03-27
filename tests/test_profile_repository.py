import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from repositories.profile_repository import ProfileRepository


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
def profile_repo(mock_db):
    return ProfileRepository(mock_db)


@pytest.fixture
def mock_profile():
    profile = MagicMock()
    profile.id = "test-profile-id"
    profile.user_id = "test-user-id"
    profile.name = "Test User"
    profile.date_of_birth = "1990-01-15"
    profile.enneagram_answers = "1,2,3,4,5"
    profile.personality_type = None
    profile.competencies = None
    profile.leadership_style = None
    profile.compatibility = None
    profile.created_at = datetime.now(timezone.utc)
    profile.updated_at = None
    return profile


@pytest.mark.asyncio
async def test_get_by_id(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await profile_repo.get_by_id("test-id")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_found(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    result = await profile_repo.get_by_id("test-id")

    assert result is not None
    assert result.name == "Test User"


@pytest.mark.asyncio
async def test_get_by_user_id(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await profile_repo.get_by_user_id("user-id")

    assert result == []


@pytest.mark.asyncio
async def test_get_by_user_and_id(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await profile_repo.get_by_user_and_id("user-id", "profile-id")

    assert result is None


@pytest.mark.asyncio
async def test_create(profile_repo, mock_db):
    result = await profile_repo.create(
        user_id="user-id",
        name="Test User",
        date_of_birth="1990-01-15",
        enneagram_answers="1,2,3,4,5",
    )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id", user_id="user-id", personality_type="Type 3"
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_competencies(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id", user_id="user-id", competencies={"leadership": 8}
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_leadership_style(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id", user_id="user-id", leadership_style="Democratic"
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_compatibility(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id", user_id="user-id", compatibility="Startups"
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_profile_synthesis(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id", user_id="user-id", profile_synthesis="Test synthesis"
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_leadership_type_json(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id",
        user_id="user-id",
        leadership_type={"archetype": "Transformational", "description": "Test desc"},
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_communication_style(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id",
        user_id="user-id",
        communication_style="Direct and clear",
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_team_role(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id", user_id="user-id", team_role="The Coordinator"
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_key_competencies(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id",
        user_id="user-id",
        key_competencies=[{"name": "Leadership", "value": 90}],
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_growth_areas(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id",
        user_id="user-id",
        growth_areas=["Communication", "Patience"],
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_all_new_fields(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.update(
        profile_id="profile-id",
        user_id="user-id",
        profile_synthesis="Full synthesis",
        leadership_type={"archetype": "Leader", "description": "Desc"},
        communication_style="Clear",
        team_role="Facilitator",
        key_competencies=[{"name": "Skill", "value": 80}],
        growth_areas=["Area1"],
    )

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(Exception):
        await profile_repo.update(
            profile_id="nonexistent", user_id="user-id", personality_type="Type 3"
        )


@pytest.mark.asyncio
async def test_delete(profile_repo, mock_db, mock_profile):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result

    await profile_repo.delete("profile-id", "user-id")

    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(Exception):
        await profile_repo.delete("nonexistent", "user-id")


@pytest.mark.asyncio
async def test_count_by_user(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 5
    mock_db.execute.return_value = mock_result

    result = await profile_repo.count_by_user("user-id")

    assert result == 5


@pytest.mark.asyncio
async def test_count_by_user_zero(profile_repo, mock_db):
    mock_result = MagicMock()
    mock_result.scalar.return_value = None
    mock_db.execute.return_value = mock_result

    result = await profile_repo.count_by_user("user-id")

    assert result == 0
