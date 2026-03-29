import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["GEMINI_API_KEY"] = "test-api-key"
os.environ["BLOCKCHAIN_RPC_URL"] = "http://localhost:8545"
os.environ["TALENT_SERVICES_CONTRACT_ADDRESS"] = ""
os.environ["TALENT_NFT_CONTRACT_ADDRESS"] = ""
os.environ["PRIVATE_KEY"] = "test-private-key"

from main import app
from core.database import Base, get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    from unittest.mock import AsyncMock

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    mock_ollama = AsyncMock()
    mock_ollama.chat.return_value = AsyncMock(
        message=AsyncMock(
            content='{"profile_synthesis": "Test synthesis", "leadership_type": {"archetype": "Transformational", "description": "Leading through vision"}, "communication_style": "Clear and direct", "team_role": "Facilitator", "key_competencies": [{"name": "Strategic Thinking", "value": 85}], "growth_areas": ["Public speaking"]}'
        )
    )
    app.state.ollama_client = mock_ollama

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"
    return client
