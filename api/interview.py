from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from core import get_current_user_id

router = APIRouter()


class InterviewQuestion(BaseModel):
    id: int
    text: str
    category: str


class InterviewAnswer(BaseModel):
    question_id: int
    transcript: str
    evaluation: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=0, le=100)


class InterviewSession(BaseModel):
    id: int
    user_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[InterviewAnswer] = []
    overall_score: Optional[int] = None


class StartInterviewRequest(BaseModel):
    language: str = "es"


class SubmitAnswerRequest(BaseModel):
    session_id: int
    question_id: int
    transcript: str
    audio_url: Optional[str] = None


MOCK_QUESTIONS_ES = [
    {
        "id": 1,
        "text": "Cuéntame sobre ti y tu experiencia profesional",
        "category": "introduction",
    },
    {
        "id": 2,
        "text": "¿Cuáles son tus fortalezas y debilidades?",
        "category": "self-awareness",
    },
    {
        "id": 3,
        "text": "Describe una situación difícil en el trabajo y cómo la resolviste",
        "category": "problem-solving",
    },
    {
        "id": 4,
        "text": "¿Por qué quieres trabajar con nosotros?",
        "category": "motivation",
    },
    {"id": 5, "text": "¿Dónde te ves en 5 años?", "category": "goals"},
    {
        "id": 6,
        "text": "Cuéntame sobre un proyecto del que estés orgulloso",
        "category": "achievements",
    },
    {
        "id": 7,
        "text": "¿Cómo manejas el estrés y la presión?",
        "category": "stress-management",
    },
    {"id": 8, "text": "Describe tu estilo de liderazgo", "category": "leadership"},
    {
        "id": 9,
        "text": "¿Qué te diferencia de otros candidatos?",
        "category": "unique-value",
    },
    {"id": 10, "text": "¿Tienes alguna pregunta para mí?", "category": "closing"},
]

MOCK_QUESTIONS_EN = [
    {
        "id": 1,
        "text": "Tell me about yourself and your professional experience",
        "category": "introduction",
    },
    {
        "id": 2,
        "text": "What are your strengths and weaknesses?",
        "category": "self-awareness",
    },
    {
        "id": 3,
        "text": "Describe a difficult situation at work and how you resolved it",
        "category": "problem-solving",
    },
    {"id": 4, "text": "Why do you want to work with us?", "category": "motivation"},
    {"id": 5, "text": "Where do you see yourself in 5 years?", "category": "goals"},
    {
        "id": 6,
        "text": "Tell me about a project you're proud of",
        "category": "achievements",
    },
    {
        "id": 7,
        "text": "How do you handle stress and pressure?",
        "category": "stress-management",
    },
    {"id": 8, "text": "Describe your leadership style", "category": "leadership"},
    {
        "id": 9,
        "text": "What sets you apart from other candidates?",
        "category": "unique-value",
    },
    {"id": 10, "text": "Do you have any questions for me?", "category": "closing"},
]


sessions_store: dict[int, InterviewSession] = {}
session_counter = 1


@router.get("/questions")
async def get_interview_questions(
    language: str = "es",
    user_id: str = Depends(get_current_user_id),
):
    """Get interview questions based on language"""
    questions = MOCK_QUESTIONS_ES if language == "es" else MOCK_QUESTIONS_EN
    return {"questions": questions, "total": len(questions)}


@router.post("/start")
async def start_interview(
    request: StartInterviewRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Start a new interview session"""
    global session_counter

    session = InterviewSession(
        id=session_counter,
        user_id=user_id,
        status="in_progress",
        started_at=datetime.utcnow(),
        questions=[],
    )
    sessions_store[session_counter] = session
    session_counter += 1

    questions = MOCK_QUESTIONS_ES if request.language == "es" else MOCK_QUESTIONS_EN

    return {
        "session_id": session.id,
        "status": session.status,
        "questions": questions,
    }


@router.post("/answer")
async def submit_answer(
    request: SubmitAnswerRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Submit an answer to an interview question"""
    session = sessions_store.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    answer = InterviewAnswer(
        question_id=request.question_id,
        transcript=request.transcript,
        evaluation="Good response",
        score=75,
    )
    session.questions.append(answer)

    is_last_question = request.question_id >= len(MOCK_QUESTIONS_ES)

    if is_last_question:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        total_score = sum(q.score or 0 for q in session.questions)
        session.overall_score = (
            total_score // len(session.questions) if session.questions else 0
        )

    return {
        "success": True,
        "question_id": request.question_id,
        "evaluation": answer.evaluation,
        "score": answer.score,
        "completed": session.status == "completed",
        "overall_score": session.overall_score,
    }


@router.get("/session/{session_id}")
async def get_session(
    session_id: int,
    user_id: str = Depends(get_current_user_id),
):
    """Get interview session details"""
    session = sessions_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return {
        "id": session.id,
        "status": session.status,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "questions_answered": len(session.questions),
        "overall_score": session.overall_score,
    }


@router.get("/history")
async def get_interview_history(
    user_id: str = Depends(get_current_user_id),
):
    """Get user's interview history"""
    user_sessions = [
        {
            "id": s.id,
            "status": s.status,
            "started_at": s.started_at,
            "completed_at": s.completed_at,
            "questions_answered": len(s.questions),
            "overall_score": s.overall_score,
        }
        for s in sessions_store.values()
        if s.user_id == user_id
    ]

    return {"sessions": user_sessions, "total": len(user_sessions)}
