import pytest


@pytest.mark.asyncio
async def test_create_matching_without_profile(auth_client):
    response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": "nonexistent-profile",
            "leader_data": "Looking for a strategic partner with technical expertise",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_matching_with_profile(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Matching Test User",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "leader_data": "Looking for a strategic partner with startup experience",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "matching" in data
    assert data["matching"]["profile_id"] == profile_id
    assert (
        data["matching"]["leader_data"]
        == "Looking for a strategic partner with startup experience"
    )


@pytest.mark.asyncio
async def test_create_matching_empty_leader_data(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Test User",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "leader_data": "",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_matching(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Get Matching Test",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    matching_response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "leader_data": "Seeking a technical co-founder",
        },
    )
    matching_id = matching_response.json()["matching"]["id"]

    response = await auth_client.get(f"/api/v1/matchings/{matching_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == matching_id
    assert data["profile_id"] == profile_id


@pytest.mark.asyncio
async def test_get_matching_not_found(auth_client):
    response = await auth_client.get("/api/v1/matchings/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_matchings_by_profile(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "List Matching Test",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "leader_data": "Looking for a partner",
        },
    )

    response = await auth_client.get(f"/api/v1/matchings/profile/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert "matchings" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_matchings_empty(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Empty Test",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    response = await auth_client.get(f"/api/v1/matchings/profile/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["matchings"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_delete_matching(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Delete Matching Test",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    matching_response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "leader_data": "Test leader data",
        },
    )
    matching_id = matching_response.json()["matching"]["id"]

    response = await auth_client.delete(f"/api/v1/matchings/{matching_id}")
    assert response.status_code == 204

    get_response = await auth_client.get(f"/api/v1/matchings/{matching_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_matching_not_found(auth_client):
    response = await auth_client.delete("/api/v1/matchings/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_matching_response_structure(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "name": "Structure Test",
            "date_of_birth": "1990-01-15",
            "enneagram_answers": "1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    matching_response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "leader_data": "Looking for a technical partner",
        },
    )
    data = matching_response.json()

    # Verify matching structure
    matching = data["matching"]
    assert "id" in matching
    assert "profile_id" in matching
    assert "leader_personality_type" in matching
    assert "leader_data" in matching
    assert "match_percentage" in matching
    assert "strengths" in matching
    assert "conflict_zones" in matching
    assert "created_at" in matching
