from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import ollama

from config import get_settings
from core import setup_logging, get_logger, init_db, close_db, AppException
from api import (
    auth_router,
    profiles_router,
    matching_router,
    health_router,
    talent_router,
    interview_router,
)
from middleware import limiter

settings = get_settings()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting TalentID API...")

    try:
        client = ollama.Client(host="http://localhost:11434")
        client.show("mistral")
        app.state.ollama_client = client
        logger.info("Ollama client initialized with Mistral")
    except Exception as e:
        logger.warning(f"Ollama client not initialized: {e}")
        app.state.ollama_client = None

    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down TalentID API...")
    await close_db()


app = FastAPI(
    title=settings.app_name,
    description="API para generar perfiles psicométricos y matching con IA",
    version=settings.app_version,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(profiles_router, prefix=settings.api_v1_prefix)
app.include_router(matching_router, prefix=settings.api_v1_prefix)
app.include_router(talent_router, prefix=settings.api_v1_prefix)
app.include_router(interview_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/api/perfil", include_in_schema=False)
@app.post("/api/perfil", include_in_schema=False)
async def legacy_perfil_endpoint(request: Request):
    return {"message": "Use /api/v1/profiles instead", "status": "deprecated"}


@app.get("/api/matching", include_in_schema=False)
@app.post("/api/matching", include_in_schema=False)
async def legacy_matching_endpoint(request: Request):
    return {"message": "Use /api/v1/matchings instead", "status": "deprecated"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
