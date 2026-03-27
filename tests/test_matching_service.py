import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from services.matching_service import MatchingService
from schemas import MatchingRequestInput, MatchingAIOutput
from core import NotFoundException


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def mock_matching_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_profile_id = AsyncMock()
    repo.count_by_profile = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_profile_repo():
    repo = AsyncMock()
    repo.get_by_user_and_id = AsyncMock()
    return repo


@pytest.fixture
def matching_service(mock_db, mock_matching_repo, mock_profile_repo):
    service = MatchingService(mock_db, gemini_client=None)
    service.matching_repo = mock_matching_repo
    service.profile_repo = mock_profile_repo
    return service


@pytest.fixture
def mock_profile():
    profile = MagicMock()
    profile.id = "test-profile-id"
    profile.user_id = "test-user-id"
    profile.personality_type = "Type 3"
    profile.leadership_style = "Transformational"
    profile.compatibility = "Fast-paced startups"
    return profile


@pytest.fixture
def mock_matching():
    matching = MagicMock()
    matching.id = "test-matching-id"
    matching.profile_id = "test-profile-id"
    matching.leader_data = "Looking for technical partner"
    matching.leader_personality_type = None
    matching.match_percentage = None
    matching.strengths = None
    matching.conflict_zones = None
    matching.created_at = datetime.now(timezone.utc)
    return matching


@pytest.fixture
def mock_gemini_client():
    client = MagicMock()
    client.models = MagicMock()
    client.models.generate_content = MagicMock()
    return client


@pytest.mark.asyncio
async def test_create_matching_profile_not_found(matching_service, mock_profile_repo):
    mock_profile_repo.get_by_user_and_id.return_value = None

    request = MatchingRequestInput(
        profile_id="nonexistent-profile", leader_data="Looking for a partner"
    )

    with pytest.raises(NotFoundException) as exc:
        await matching_service.create_matching("test-user-id", request)

    assert "Profile not found" in str(exc.value)


@pytest.mark.asyncio
async def test_create_matching_without_ai(
    matching_service, mock_matching_repo, mock_profile_repo, mock_profile, mock_matching
):
    mock_profile_repo.get_by_user_and_id.return_value = mock_profile
    mock_matching_repo.create.return_value = mock_matching

    request = MatchingRequestInput(
        profile_id="test-profile-id", leader_data="Looking for a technical partner"
    )

    result = await matching_service.create_matching("test-user-id", request)

    assert result.matching.profile_id == "test-profile-id"
    assert result.ai_response is None


@pytest.mark.asyncio
async def test_create_matching_with_ai(
    matching_service, mock_matching_repo, mock_profile_repo, mock_gemini_client
):
    matching_service.gemini_client = mock_gemini_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.personality_type = "Type 3"
    mock_profile.leadership_style = "Transformational"
    mock_profile.compatibility = "Startups"

    mock_matching = MagicMock()
    mock_matching.id = "test-matching-id"
    mock_matching.profile_id = "test-profile-id"
    mock_matching.leader_data = "Test"
    mock_matching.leader_personality_type = None
    mock_matching.match_percentage = None
    mock_matching.strengths = None
    mock_matching.conflict_zones = None
    mock_matching.created_at = datetime.now(timezone.utc)

    mock_profile_repo.get_by_user_and_id.return_value = mock_profile
    mock_matching_repo.create.return_value = mock_matching

    mock_response = MagicMock()
    mock_response.text = """{"match_percentage": 85, "strengths": ["Complementary skills", "Shared vision", "Growth mindset"], "conflict_zones": ["Decision making", "Work pace"]}"""
    mock_gemini_client.models.generate_content.return_value = mock_response

    request = MatchingRequestInput(
        profile_id="test-profile-id", leader_data="Looking for a partner"
    )

    result = await matching_service.create_matching("test-user-id", request)

    assert result.ai_response is not None
    assert result.ai_response.match_percentage == 85


@pytest.mark.asyncio
async def test_create_matching_ai_error(
    matching_service, mock_matching_repo, mock_profile_repo, mock_gemini_client
):
    matching_service.gemini_client = mock_gemini_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.personality_type = "Type 3"

    mock_matching = MagicMock()
    mock_matching.id = "test-matching-id"
    mock_matching.profile_id = "test-profile-id"
    mock_matching.leader_data = "Looking for partner"
    mock_matching.leader_personality_type = None
    mock_matching.match_percentage = None
    mock_matching.strengths = None
    mock_matching.conflict_zones = None

    mock_profile_repo.get_by_user_and_id.return_value = mock_profile
    mock_matching_repo.create.return_value = mock_matching
    mock_gemini_client.models.generate_content.side_effect = Exception("API Error")

    request = MatchingRequestInput(
        profile_id="test-profile-id", leader_data="Looking for partner"
    )

    result = await matching_service.create_matching("test-user-id", request)

    assert result.matching.id == "test-matching-id"
    assert result.ai_response is None


@pytest.mark.asyncio
async def test_create_matching_no_ai_when_no_personality(
    matching_service, mock_matching_repo, mock_profile_repo
):
    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.personality_type = None

    mock_matching = MagicMock()
    mock_matching.id = "test-matching-id"
    mock_matching.profile_id = "test-profile-id"
    mock_matching.leader_data = "Looking for partner"
    mock_matching.leader_personality_type = None
    mock_matching.match_percentage = None
    mock_matching.strengths = None
    mock_matching.conflict_zones = None

    mock_profile_repo.get_by_user_and_id.return_value = mock_profile
    mock_matching_repo.create.return_value = mock_matching

    request = MatchingRequestInput(
        profile_id="test-profile-id", leader_data="Looking for partner"
    )

    result = await matching_service.create_matching("test-user-id", request)

    assert result.ai_response is None


@pytest.mark.asyncio
async def test_get_matching_success(
    matching_service, mock_matching_repo, mock_matching
):
    mock_matching_repo.get_by_id.return_value = mock_matching

    result = await matching_service.get_matching("test-matching-id")

    assert result.id == "test-matching-id"


@pytest.mark.asyncio
async def test_get_matching_not_found(matching_service, mock_matching_repo):
    mock_matching_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException) as exc:
        await matching_service.get_matching("nonexistent-id")

    assert "Matching not found" in str(exc.value)


@pytest.mark.asyncio
async def test_list_matchings(matching_service, mock_matching_repo, mock_matching):
    mock_matching_repo.get_by_profile_id.return_value = [mock_matching]
    mock_matching_repo.count_by_profile.return_value = 1

    result = await matching_service.list_matchings("test-profile-id")

    assert result.total == 1
    assert len(result.matchings) == 1


@pytest.mark.asyncio
async def test_list_matchings_empty(matching_service, mock_matching_repo):
    mock_matching_repo.get_by_profile_id.return_value = []
    mock_matching_repo.count_by_profile.return_value = 0

    result = await matching_service.list_matchings("test-profile-id")

    assert result.total == 0
    assert result.matchings == []


@pytest.mark.asyncio
async def test_delete_matching(matching_service, mock_matching_repo):
    await matching_service.delete_matching("test-matching-id")
    mock_matching_repo.delete.assert_called_once_with("test-matching-id")


@pytest.mark.asyncio
async def test_create_matching_with_ai_json_prefix(
    matching_service, mock_matching_repo, mock_profile_repo, mock_gemini_client
):
    matching_service.gemini_client = mock_gemini_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.personality_type = "Type 3"
    mock_profile.leadership_style = "Transformational"
    mock_profile.compatibility = "Startups"

    mock_matching = MagicMock()
    mock_matching.id = "test-matching-id"
    mock_matching.profile_id = "test-profile-id"
    mock_matching.leader_data = "Test"
    mock_matching.leader_personality_type = None
    mock_matching.match_percentage = None
    mock_matching.strengths = None
    mock_matching.conflict_zones = None

    mock_profile_repo.get_by_user_and_id.return_value = mock_profile
    mock_matching_repo.create.return_value = mock_matching

    mock_response = MagicMock()
    mock_response.text = """```json
{"match_percentage": 85, "strengths": ["Complementary skills"], "conflict_zones": ["Decision making"]}
```"""
    mock_gemini_client.models.generate_content.return_value = mock_response

    request = MatchingRequestInput(
        profile_id="test-profile-id", leader_data="Looking for a partner"
    )

    result = await matching_service.create_matching("test-user-id", request)

    assert result.ai_response is not None
    assert result.ai_response.match_percentage == 85


@pytest.mark.asyncio
async def test_create_matching_with_ai_markdown_prefix(
    matching_service, mock_matching_repo, mock_profile_repo, mock_gemini_client
):
    matching_service.gemini_client = mock_gemini_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.personality_type = "Type 3"
    mock_profile.leadership_style = "Transformational"
    mock_profile.compatibility = "Startups"

    mock_matching = MagicMock()
    mock_matching.id = "test-matching-id"
    mock_matching.profile_id = "test-profile-id"
    mock_matching.leader_data = "Test"
    mock_matching.leader_personality_type = None
    mock_matching.match_percentage = None
    mock_matching.strengths = None
    mock_matching.conflict_zones = None

    mock_profile_repo.get_by_user_and_id.return_value = mock_profile
    mock_matching_repo.create.return_value = mock_matching

    mock_response = MagicMock()
    mock_response.text = '```\n{"match_percentage": 80, "strengths": ["Vision"], "conflict_zones": ["Pace"]}\n```'
    mock_gemini_client.models.generate_content.return_value = mock_response

    request = MatchingRequestInput(
        profile_id="test-profile-id", leader_data="Looking for a partner"
    )

    result = await matching_service.create_matching("test-user-id", request)

    assert result.ai_response is not None
    assert result.ai_response.match_percentage == 80
