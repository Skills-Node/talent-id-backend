import pytest


@pytest.mark.asyncio
class TestInterviewQuestions:
    async def test_get_questions_spanish_default(self, auth_client):
        response = await auth_client.get("/api/v1/interview/questions")
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert data["total"] == 10
        assert (
            data["questions"][0]["text"]
            == "Cuéntame sobre ti y tu experiencia profesional"
        )

    async def test_get_questions_english(self, auth_client):
        response = await auth_client.get("/api/v1/interview/questions?language=en")
        assert response.status_code == 200
        data = response.json()
        assert (
            data["questions"][0]["text"]
            == "Tell me about yourself and your professional experience"
        )

    async def test_get_questions_unauthorized(self, client):
        response = await client.get("/api/v1/interview/questions")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestInterviewStart:
    async def test_start_interview_spanish(self, auth_client):
        response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "in_progress"
        assert "questions" in data

    async def test_start_interview_english(self, auth_client):
        response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "en"},
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            data["questions"][0]["text"]
            == "Tell me about yourself and your professional experience"
        )

    async def test_start_interview_default_language(self, auth_client):
        response = await auth_client.post(
            "/api/v1/interview/start",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            data["questions"][0]["text"]
            == "Cuéntame sobre ti y tu experiencia profesional"
        )

    async def test_start_interview_unauthorized(self, client):
        response = await client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestInterviewSubmitAnswer:
    async def test_submit_answer_success(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        response = await auth_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": session_id,
                "question_id": 1,
                "transcript": "Soy un profesional con 5 años de experiencia...",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["question_id"] == 1
        assert "evaluation" in data
        assert "score" in data
        assert data["completed"] is False

    async def test_submit_answer_with_audio_url(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        response = await auth_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": session_id,
                "question_id": 1,
                "transcript": "Test answer",
                "audio_url": "https://example.com/audio.mp3",
            },
        )
        assert response.status_code == 200

    async def test_submit_answer_completes_interview(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        for question_id in range(1, 11):
            response = await auth_client.post(
                "/api/v1/interview/answer",
                json={
                    "session_id": session_id,
                    "question_id": question_id,
                    "transcript": f"Answer to question {question_id}",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        assert data["overall_score"] is not None

    async def test_submit_answer_session_not_found(self, auth_client):
        response = await auth_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": 99999,
                "question_id": 1,
                "transcript": "Test answer",
            },
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    async def test_submit_answer_not_authorized(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        other_client = auth_client
        other_client.headers["Authorization"] = "Bearer invalid_token"
        response = await other_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": session_id,
                "question_id": 1,
                "transcript": "Test answer",
            },
        )
        assert response.status_code == 401

    async def test_submit_answer_unauthorized_for_session(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        # Remove auth header to test unauthorized access
        original_auth = auth_client.headers.get("Authorization")
        del auth_client.headers["Authorization"]

        response = await auth_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": session_id,
                "question_id": 1,
                "transcript": "Test answer",
            },
        )

        # Restore auth header
        if original_auth:
            auth_client.headers["Authorization"] = original_auth

        assert response.status_code == 401


@pytest.mark.asyncio
class TestInterviewSession:
    async def test_get_session_success(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        response = await auth_client.get(f"/api/v1/interview/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["status"] == "in_progress"
        assert "started_at" in data

    async def test_get_session_not_found(self, auth_client):
        response = await auth_client.get("/api/v1/interview/session/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    async def test_get_session_unauthorized(self, client):
        response = await client.get("/api/v1/interview/session/1")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestInterviewHistory:
    async def test_get_history_empty(self, auth_client):
        response = await auth_client.get("/api/v1/interview/history")
        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []
        assert data["total"] == 0

    async def test_get_history_with_sessions(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        for question_id in range(1, 11):
            await auth_client.post(
                "/api/v1/interview/answer",
                json={
                    "session_id": session_id,
                    "question_id": question_id,
                    "transcript": f"Answer {question_id}",
                },
            )

        response = await auth_client.get("/api/v1/interview/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["sessions"][0]["status"] == "completed"
        assert data["sessions"][0]["overall_score"] is not None

    async def test_get_history_multiple_sessions(self, auth_client):
        for _ in range(3):
            start_response = await auth_client.post(
                "/api/v1/interview/start",
                json={"language": "es"},
            )
            session_id = start_response.json()["session_id"]

            for question_id in range(1, 11):
                await auth_client.post(
                    "/api/v1/interview/answer",
                    json={
                        "session_id": session_id,
                        "question_id": question_id,
                        "transcript": "Answer",
                    },
                )

        response = await auth_client.get("/api/v1/interview/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    async def test_get_history_unauthorized(self, client):
        response = await client.get("/api/v1/interview/history")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestInterviewEdgeCases:
    async def test_questions_have_correct_categories(self, auth_client):
        response = await auth_client.get("/api/v1/interview/questions")
        data = response.json()
        categories = {q["category"] for q in data["questions"]}
        expected_categories = {
            "introduction",
            "self-awareness",
            "problem-solving",
            "motivation",
            "goals",
            "achievements",
            "stress-management",
            "leadership",
            "unique-value",
            "closing",
        }
        assert categories == expected_categories

    async def test_questions_have_ids(self, auth_client):
        response = await auth_client.get("/api/v1/interview/questions")
        data = response.json()
        ids = [q["id"] for q in data["questions"]]
        assert ids == list(range(1, 11))

    async def test_interview_session_persists_answers(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        await auth_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": session_id,
                "question_id": 1,
                "transcript": "First answer",
            },
        )

        session_response = await auth_client.get(
            f"/api/v1/interview/session/{session_id}"
        )
        data = session_response.json()
        assert data["questions_answered"] == 1

    async def test_answer_score_range(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        session_id = start_response.json()["session_id"]

        response = await auth_client.post(
            "/api/v1/interview/answer",
            json={
                "session_id": session_id,
                "question_id": 1,
                "transcript": "Test",
            },
        )
        data = response.json()
        assert 0 <= data["score"] <= 100


@pytest.mark.asyncio
class TestInterviewL3Advanced:
    async def test_full_interview_flow(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "es"},
        )
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]

        questions_response = await auth_client.get("/api/v1/interview/questions")
        assert questions_response.status_code == 200

        for i in range(1, 11):
            answer_response = await auth_client.post(
                "/api/v1/interview/answer",
                json={
                    "session_id": session_id,
                    "question_id": i,
                    "transcript": f"My answer to question {i}",
                },
            )
            assert answer_response.status_code == 200

        final_session = await auth_client.get(f"/api/v1/interview/session/{session_id}")
        assert final_session.json()["status"] == "completed"

        history = await auth_client.get("/api/v1/interview/history")
        assert history.json()["total"] == 1

    async def test_concurrent_interview_sessions(self, auth_client):
        sessions = []
        for _ in range(3):
            response = await auth_client.post(
                "/api/v1/interview/start",
                json={"language": "es"},
            )
            sessions.append(response.json()["session_id"])

        for session_id in sessions:
            response = await auth_client.get(f"/api/v1/interview/session/{session_id}")
            assert response.status_code == 200

        history = await auth_client.get("/api/v1/interview/history")
        assert history.json()["total"] == 3

    async def test_english_interview_flow(self, auth_client):
        start_response = await auth_client.post(
            "/api/v1/interview/start",
            json={"language": "en"},
        )
        session_id = start_response.json()["session_id"]

        for i in range(1, 11):
            await auth_client.post(
                "/api/v1/interview/answer",
                json={
                    "session_id": session_id,
                    "question_id": i,
                    "transcript": f"My answer to question {i}",
                },
            )

        final_session = await auth_client.get(f"/api/v1/interview/session/{session_id}")
        data = final_session.json()
        assert data["status"] == "completed"
        assert data["questions_answered"] == 10
