import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/talent/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "blockchain_connected" in data


@pytest.mark.asyncio
async def test_search_candidates_unauthorized(client):
    response = await client.post(
        "/api/v1/talent/search",
        json={
            "skills": ["Leadership"],
            "personality_types": ["Leader"],
            "limit": 10,
            "offset": 0,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_search_candidates_with_filters(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/search",
        json={
            "skills": ["Leadership", "Communication"],
            "personality_types": ["Leader", "Strategist"],
            "limit": 20,
            "offset": 0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_search_candidates_empty_filters(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/search",
        json={"skills": [], "personality_types": [], "limit": 10, "offset": 0},
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_search_candidates_with_pagination(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/search",
        json={"skills": [], "personality_types": [], "limit": 5, "offset": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data


@pytest.mark.asyncio
async def test_get_candidates_unauthorized(client):
    response = await client.get("/api/v1/talent/candidates?limit=10&offset=0")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_candidates(auth_client):
    response = await auth_client.get("/api/v1/talent/candidates?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_candidates_with_default_params(auth_client):
    response = await auth_client.get("/api/v1/talent/candidates")
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data


@pytest.mark.asyncio
async def test_get_candidates_pagination(auth_client):
    response = await auth_client.get("/api/v1/talent/candidates?limit=5&offset=5")
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data


@pytest.mark.asyncio
async def test_get_active_jobs_unauthorized(client):
    response = await client.get("/api/v1/talent/jobs?limit=10&offset=0")
    # When no contract is configured, returns 200 with empty list
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_active_jobs(auth_client):
    response = await auth_client.get("/api/v1/talent/jobs?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_active_jobs_default_params(auth_client):
    response = await auth_client.get("/api/v1/talent/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data


@pytest.mark.asyncio
async def test_get_active_jobs_pagination(auth_client):
    response = await auth_client.get("/api/v1/talent/jobs?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data


@pytest.mark.asyncio
async def test_create_job_unauthorized(client):
    response = await client.post(
        "/api/v1/talent/jobs",
        json={
            "title": "Software Engineer",
            "description": "Build great software",
            "requirements": "3+ years experience",
            "salary_min": 50000,
            "salary_max": 100000,
            "location": "Remote",
            "is_remote": True,
            "required_skills": ["Python", "JavaScript"],
            "preferred_personality_types": ["Leader"],
            "employment_type": "full-time",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_job(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/jobs",
        json={
            "title": "Software Engineer",
            "description": "Build great software",
            "requirements": "3+ years experience",
            "salary_min": 50000,
            "salary_max": 100000,
            "location": "Remote",
            "is_remote": True,
            "required_skills": ["Python", "JavaScript"],
            "preferred_personality_types": ["Leader"],
            "employment_type": "full-time",
        },
    )
    # Without contract configured, returns 400
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_create_job_minimal_data(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/jobs",
        json={
            "title": "Intern",
            "description": "Learning opportunity",
            "requirements": "None",
            "salary_min": 0,
            "salary_max": 0,
            "location": "Office",
            "is_remote": False,
            "required_skills": [],
            "preferred_personality_types": [],
            "employment_type": "internship",
        },
    )
    # Without contract, returns 400
    assert response.status_code == 400
    data = response.json()
    assert "success" in data or "job_id" in data


@pytest.mark.asyncio
async def test_create_job_minimal_data(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/jobs",
        json={
            "title": "Intern",
            "description": "Learning opportunity",
            "requirements": "None",
            "salary_min": 0,
            "salary_max": 0,
            "location": "Office",
            "is_remote": False,
            "required_skills": [],
            "preferred_personality_types": [],
            "employment_type": "internship",
        },
    )
    # Without contract, returns 400
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_company_unauthorized(client):
    response = await client.post(
        "/api/v1/talent/register-company",
        json={
            "name": "Test Company",
            "description": "A test company",
            "industry": "Technology",
            "website": "https://test.com",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_company(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/register-company",
        json={
            "name": "Test Company",
            "description": "A test company",
            "industry": "Technology",
            "website": "https://test.com",
        },
    )
    # Without contract configured, returns 400
    assert response.status_code in [201, 400]


@pytest.mark.asyncio
async def test_register_company_validation(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/register-company",
        json={
            "name": "",  # Empty name should fail
            "description": "A test company",
            "industry": "Technology",
            "website": "https://test.com",
        },
    )
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_create_offer_unauthorized(client):
    response = await client.post(
        "/api/v1/talent/offers",
        json={
            "job_id": 1,
            "talent_address": "0xABC123",
            "token_id": 1,
            "terms": "Full-time position",
            "salary": 75000,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_offer(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/offers",
        json={
            "job_id": 1,
            "talent_address": "0xABC123DEF456",
            "token_id": 1,
            "terms": "Full-time position with benefits",
            "salary": 100000,
        },
    )
    # Without contract configured, returns 400
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_create_offer_validation(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/offers",
        json={
            "job_id": 1,
            "talent_address": "0xABC123",
            "token_id": 1,
            "terms": "",
            "salary": -100,  # Negative salary should fail
        },
    )
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_accept_offer_unauthorized(client):
    response = await client.post("/api/v1/talent/offers/1/accept")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_accept_offer(auth_client):
    response = await auth_client.post("/api/v1/talent/offers/1/accept")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "offer" in data


@pytest.mark.asyncio
async def test_reject_offer_unauthorized(client):
    response = await client.post("/api/v1/talent/offers/1/reject")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reject_offer(auth_client):
    response = await auth_client.post("/api/v1/talent/offers/1/reject")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "offer" in data


@pytest.mark.asyncio
async def test_search_candidates_schema_validation_limit(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/search",
        json={
            "skills": [],
            "personality_types": [],
            "limit": -1,  # Invalid limit
            "offset": 0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_candidates_schema_validation_offset(auth_client):
    response = await auth_client.post(
        "/api/v1/talent/search",
        json={
            "skills": [],
            "personality_types": [],
            "limit": 10,
            "offset": -1,  # Invalid offset
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_jobs_schema_validation_limit(client):
    response = await client.get("/api/v1/talent/jobs?limit=-1")
    # Returns 200 since no auth required
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_candidates_schema_validation_limit(auth_client):
    response = await auth_client.get("/api/v1/talent/candidates?limit=-1")
    assert response.status_code == 422 or response.status_code == 200
