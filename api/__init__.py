from api.auth import router as auth_router
from api.profiles import router as profiles_router
from api.matching import router as matching_router
from api.health import router as health_router
from api.talent import router as talent_router
from api.interview import router as interview_router

__all__ = [
    "auth_router",
    "profiles_router",
    "matching_router",
    "health_router",
    "talent_router",
    "interview_router",
]
