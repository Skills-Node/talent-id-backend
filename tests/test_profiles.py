import pytest


@pytest.mark.asyncio
async def test_create_profile(auth_client):
    response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "John Smith",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,3,2,1,1,2,3,4,5,4,3,2,1,5,4,3,2,1,3,4,5,4,3",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "profile" in data
    assert data["profile"]["name"] == "John Smith"
    assert "ai_response" in data


@pytest.mark.asyncio
async def test_create_profile_unauthorized(client):
    response = await client.post(
        "/api/v1/profiles",
        json={
            "name": "John Smith",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_profile_invalid_date(auth_client):
    response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Test User",
            "date_of_birth": "invalid-date",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    # Should still work, date is stored as string
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_profile_empty_answers(auth_client):
    response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Test User",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_profiles(auth_client):
    await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Test User",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )

    response = await auth_client.get("/api/v1/profiles")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_profiles_empty(auth_client):
    response = await auth_client.get("/api/v1/profiles")
    assert response.status_code == 200
    data = response.json()
    assert data["profiles"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_profile(auth_client):
    create_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Get Test User",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = create_response.json()["profile"]["id"]

    response = await auth_client.get(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get Test User"
    assert data["date_of_birth"] == "1990-01-15"


@pytest.mark.asyncio
async def test_get_profile_not_found(auth_client):
    response = await auth_client.get("/api/v1/profiles/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_profile(auth_client):
    create_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Delete Test User",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = create_response.json()["profile"]["id"]

    response = await auth_client.delete(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 204

    get_response = await auth_client.get(f"/api/v1/profiles/{profile_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_profile_not_found(auth_client):
    response = await auth_client.delete("/api/v1/profiles/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_profile_response_structure(auth_client):
    create_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Structure Test",
            "date_of_birth": "1985-06-20",
            "enneagram_answers": "5,4,3,2,1,5,4,3,2,1,5,4,3,2,1,5,4,3,2,1,5,4,3,2,1",
        },
    )
    data = create_response.json()

    # Verify profile structure
    profile = data["profile"]
    assert "id" in profile
    assert "user_id" in profile
    assert "name" in profile
    assert "date_of_birth" in profile
    assert "enneagram_answers" in profile
    assert "personality_type" in profile
    assert "competencies" in profile
    assert "leadership_style" in profile
    assert "compatibility" in profile
    assert "created_at" in profile
    assert "updated_at" in profile
