import pytest


@pytest.mark.asyncio
async def test_create_matching_without_profile(auth_client):
    response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": "nonexistent-profile",
            "datos_lider": "Líder tipo A con experiencia en startups",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_matching_with_profile(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Matching Test",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "datos_lider": "Líder tipo A con experiencia en startups",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "matching" in data
    assert data["matching"]["profile_id"] == profile_id


@pytest.mark.asyncio
async def test_get_matching(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Get Matching Test",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    matching_response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "datos_lider": "Líder test",
        },
    )
    matching_id = matching_response.json()["matching"]["id"]

    response = await auth_client.get(f"/api/v1/matchings/{matching_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == matching_id


@pytest.mark.asyncio
async def test_list_matchings_by_profile(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "List Matching Test",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "datos_lider": "Líder test",
        },
    )

    response = await auth_client.get(f"/api/v1/matchings/profile/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert "matchings" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_delete_matching(auth_client):
    profile_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Delete Matching Test",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    profile_id = profile_response.json()["profile"]["id"]

    matching_response = await auth_client.post(
        "/api/v1/matchings",
        json={
            "profile_id": profile_id,
            "datos_lider": "Líder test",
        },
    )
    matching_id = matching_response.json()["matching"]["id"]

    response = await auth_client.delete(f"/api/v1/matchings/{matching_id}")
    assert response.status_code == 204
