import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from services.profile_service import ProfileService
from schemas import ProfileRequestInput, ProfileAIOutput, Competency
from core import NotFoundException


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_profile_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_by_user_and_id = AsyncMock()
    repo.get_by_user_id = AsyncMock()
    repo.count_by_user = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def profile_service(mock_db, mock_profile_repo):
    service = ProfileService(mock_db, ollama_client=None)
    service.profile_repo = mock_profile_repo
    return service


@pytest.fixture
def mock_profile():
    profile = MagicMock()
    profile.id = "test-profile-id"
    profile.user_id = "test-user-id"
    profile.name = "Test User"
    profile.date_of_birth = "1990-01-15"
    profile.enneagram_answers = "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5"
    profile.personality_type = None
    profile.profile_synthesis = None
    profile.leadership_type = None
    profile.communication_style = None
    profile.team_role = None
    profile.key_competencies = None
    profile.growth_areas = None
    profile.competencies = None
    profile.leadership_style = None
    profile.compatibility = None
    profile.created_at = datetime.now(timezone.utc)
    profile.updated_at = None
    return profile


@pytest.fixture
def mock_ollama_client():
    client = MagicMock()
    client.chat = MagicMock()
    return client


@pytest.mark.asyncio
async def test_create_profile_without_ai(
    profile_service, mock_profile_repo, mock_profile
):
    mock_profile_repo.create.return_value = mock_profile

    request = ProfileRequestInput(
        name="Test User",
        date_of_birth="1990-01-15",
        enneagram_answers="1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
    )

    result = await profile_service.create_profile("test-user-id", request)

    assert result.profile.name == "Test User"
    assert result.ai_response is None
    mock_profile_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_profile_with_ai(
    profile_service, mock_profile_repo, mock_ollama_client
):
    profile_service.ollama_client = mock_ollama_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.name = "Test User"
    mock_profile.date_of_birth = "1990-01-15"
    mock_profile.enneagram_answers = "1,2,3,4,5"
    mock_profile.personality_type = None
    mock_profile.profile_synthesis = None
    mock_profile.leadership_type = None
    mock_profile.communication_style = None
    mock_profile.team_role = None
    mock_profile.key_competencies = None
    mock_profile.growth_areas = None
    mock_profile.competencies = None
    mock_profile.leadership_style = None
    mock_profile.compatibility = None
    mock_profile.created_at = datetime.now(timezone.utc)
    mock_profile.updated_at = None

    mock_profile_repo.create.return_value = mock_profile
    mock_profile_repo.update.return_value = mock_profile

    mock_ollama_client.chat.return_value = {
        "message": {
            "content": """{"profile_synthesis": "This is a deep synthesis...", "leadership_type": {"archetype": "Transformational", "description": "Leaders who inspire"}, "communication_style": "Direct", "team_role": "Integrator", "key_competencies": [{"name": "Leadership", "value": 85}, {"name": "Communication", "value": 90}], "growth_areas": ["Patience"]}"""
        }
    }

    request = ProfileRequestInput(
        name="Test User", date_of_birth="1990-01-15", enneagram_answers="1,2,3,4,5"
    )

    result = await profile_service.create_profile("test-user-id", request)

    mock_profile_repo.update.assert_called_once()
    assert result.ai_response is None


@pytest.mark.asyncio
async def test_create_profile_ai_error(
    profile_service, mock_profile_repo, mock_ollama_client
):
    profile_service.ollama_client = mock_ollama_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.name = "Test User"
    mock_profile.date_of_birth = "1990-01-15"
    mock_profile.enneagram_answers = "1,2,3,4,5"
    mock_profile.personality_type = None
    mock_profile.profile_synthesis = None
    mock_profile.leadership_type = None
    mock_profile.communication_style = None
    mock_profile.team_role = None
    mock_profile.key_competencies = None
    mock_profile.growth_areas = None
    mock_profile.competencies = None
    mock_profile.leadership_style = None
    mock_profile.compatibility = None
    mock_profile.created_at = datetime.now(timezone.utc)
    mock_profile.updated_at = None

    mock_profile_repo.create.return_value = mock_profile

    mock_ollama_client.chat.side_effect = Exception("API Error")

    request = ProfileRequestInput(
        name="Test User", date_of_birth="1990-01-15", enneagram_answers="1,2,3,4,5"
    )

    result = await profile_service.create_profile("test-user-id", request)

    assert result.profile.name == "Test User"
    assert result.ai_response is None


@pytest.mark.asyncio
async def test_get_profile_success(profile_service, mock_profile_repo, mock_profile):
    mock_profile_repo.get_by_user_and_id.return_value = mock_profile

    result = await profile_service.get_profile("test-user-id", "test-profile-id")

    assert result.id == "test-profile-id"
    assert result.name == "Test User"


@pytest.mark.asyncio
async def test_get_profile_not_found(profile_service, mock_profile_repo):
    mock_profile_repo.get_by_user_and_id.return_value = None

    with pytest.raises(NotFoundException) as exc:
        await profile_service.get_profile("test-user-id", "nonexistent-id")

    assert "Profile not found" in str(exc.value)


@pytest.mark.asyncio
async def test_list_profiles(profile_service, mock_profile_repo):
    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.name = "Test User"
    mock_profile.date_of_birth = "1990-01-15"
    mock_profile.enneagram_answers = "1,2,3,4,5"
    mock_profile.personality_type = None
    mock_profile.profile_synthesis = None
    mock_profile.leadership_type = None
    mock_profile.communication_style = None
    mock_profile.team_role = None
    mock_profile.key_competencies = None
    mock_profile.growth_areas = None
    mock_profile.competencies = None
    mock_profile.leadership_style = None
    mock_profile.compatibility = None
    mock_profile.created_at = datetime.now(timezone.utc)
    mock_profile.updated_at = None

    mock_profile_repo.get_by_user_id.return_value = [mock_profile]
    mock_profile_repo.count_by_user.return_value = 1

    result = await profile_service.list_profiles("test-user-id")

    assert result.total == 1
    assert len(result.profiles) == 1


@pytest.mark.asyncio
async def test_list_profiles_empty(profile_service, mock_profile_repo):
    mock_profile_repo.get_by_user_id.return_value = []
    mock_profile_repo.count_by_user.return_value = 0

    result = await profile_service.list_profiles("test-user-id")

    assert result.total == 0
    assert result.profiles == []


@pytest.mark.asyncio
async def test_delete_profile(profile_service, mock_profile_repo):
    await profile_service.delete_profile("test-user-id", "test-profile-id")

    mock_profile_repo.delete.assert_called_once_with("test-profile-id", "test-user-id")


@pytest.mark.asyncio
async def test_create_profile_with_ai_json_prefix(
    profile_service, mock_profile_repo, mock_ollama_client
):
    profile_service.ollama_client = mock_ollama_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.name = "Test User"
    mock_profile.date_of_birth = "1990-01-15"
    mock_profile.enneagram_answers = "1,2,3,4,5"
    mock_profile.personality_type = None
    mock_profile.profile_synthesis = None
    mock_profile.leadership_type = None
    mock_profile.communication_style = None
    mock_profile.team_role = None
    mock_profile.key_competencies = None
    mock_profile.growth_areas = None
    mock_profile.competencies = None
    mock_profile.leadership_style = None
    mock_profile.compatibility = None

    mock_profile_repo.create.return_value = mock_profile
    mock_profile_repo.update.return_value = mock_profile

    mock_ollama_client.chat.return_value = {
        "message": {
            "content": """```json
{"profile_synthesis": "This is a deep synthesis...", "leadership_type": {"archetype": "Transformational", "description": "Leaders who inspire"}, "communication_style": "Direct", "team_role": "Integrator", "key_competencies": [{"name": "Leadership", "value": 85}, {"name": "Communication", "value": 90}], "growth_areas": ["Patience"]}
```"""
        }
    }

    request = ProfileRequestInput(
        name="Test User", date_of_birth="1990-01-15", enneagram_answers="1,2,3,4,5"
    )

    result = await profile_service.create_profile("test-user-id", request)

    assert result.ai_response is None


@pytest.mark.asyncio
async def test_create_profile_with_ai_markdown_prefix(
    profile_service, mock_profile_repo, mock_ollama_client
):
    profile_service.ollama_client = mock_ollama_client

    mock_profile = MagicMock()
    mock_profile.id = "test-profile-id"
    mock_profile.user_id = "test-user-id"
    mock_profile.name = "Test User"
    mock_profile.date_of_birth = "1990-01-15"
    mock_profile.enneagram_answers = "1,2,3,4,5"
    mock_profile.personality_type = None
    mock_profile.profile_synthesis = None
    mock_profile.leadership_type = None
    mock_profile.communication_style = None
    mock_profile.team_role = None
    mock_profile.key_competencies = None
    mock_profile.growth_areas = None
    mock_profile.competencies = None
    mock_profile.leadership_style = None
    mock_profile.compatibility = None

    mock_profile_repo.create.return_value = mock_profile
    mock_profile_repo.update.return_value = mock_profile

    mock_ollama_client.chat.return_value = {
        "message": {
            "content": '```\n{"profile_synthesis": "This is a synthesis...", "leadership_type": {"archetype": "Autocratic", "description": "Direct leadership"}, "communication_style": "Brief", "team_role": "Leader", "key_competencies": [{"name": "Vision", "value": 80}], "growth_areas": ["Flexibility"]}\n```'
        }
    }

    request = ProfileRequestInput(
        name="Test User", date_of_birth="1990-01-15", enneagram_answers="1,2,3,4,5"
    )

    result = await profile_service.create_profile("test-user-id", request)

    assert result.ai_response is None
