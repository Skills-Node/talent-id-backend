import pytest


@pytest.mark.asyncio
async def test_create_profile(auth_client):
    response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Juan Pérez",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "profile" in data
    assert data["profile"]["nombre"] == "Juan Pérez"
    assert "ai_response" in data


@pytest.mark.asyncio
async def test_create_profile_unauthorized(client):
    response = await client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Juan Pérez",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_profiles(auth_client):
    await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Test User",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )

    response = await auth_client.get("/api/v1/profiles")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_profile(auth_client):
    create_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Get Test",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    profile_id = create_response.json()["profile"]["id"]

    response = await auth_client.get(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Get Test"


@pytest.mark.asyncio
async def test_get_profile_not_found(auth_client):
    response = await auth_client.get("/api/v1/profiles/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_profile(auth_client):
    create_response = await auth_client.post(
        "/api/v1/profiles",
        json={
            "nombre": "Delete Test",
            "fecha_nacimiento": "1990-01-15",
            "respuestas_eneagrama": "123321123",
        },
    )
    profile_id = create_response.json()["profile"]["id"]

    response = await auth_client.delete(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 204

    get_response = await auth_client.get(f"/api/v1/profiles/{profile_id}")
    assert get_response.status_code == 404
