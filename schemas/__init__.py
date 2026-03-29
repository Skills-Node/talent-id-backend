from schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    TokenPayload,
)
from schemas.profile import (
    Competency,
    ProfileRequestInput,
    ProfileAIOutput,
    ProfileResponse,
    ProfileListResponse,
    ProfileCreateResponse,
    TalentProfile,
    LeadershipType,
)
from schemas.matching import (
    MatchingRequestInput,
    MatchingAIOutput,
    MatchingResponse,
    MatchingListResponse,
    MatchingCreateResponse,
)
from schemas.talent_service import (
    CompanyCreate,
    CompanyResponse,
    JobCreate,
    JobResponse,
    JobListResponse,
    CandidateSearchRequest,
    CandidateResponse,
    CandidateListResponse,
    OfferCreate,
    OfferResponse,
    OfferListResponse,
    OfferActionResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "RefreshTokenRequest",
    "TokenPayload",
    # Profile schemas (English)
    "Competency",
    "ProfileRequestInput",
    "ProfileAIOutput",
    "ProfileResponse",
    "ProfileListResponse",
    "ProfileCreateResponse",
    "TalentProfileOutput",
    "LeadershipType",
    # Matching schemas (English)
    "MatchingRequestInput",
    "MatchingAIOutput",
    "MatchingResponse",
    "MatchingListResponse",
    "MatchingCreateResponse",
    # Talent Service schemas
    "CompanyCreate",
    "CompanyResponse",
    "JobCreate",
    "JobResponse",
    "JobListResponse",
    "CandidateSearchRequest",
    "CandidateResponse",
    "CandidateListResponse",
    "OfferCreate",
    "OfferResponse",
    "OfferListResponse",
    "OfferActionResponse",
]

# Spanish aliases for backward compatibility
Competencia = Competency
PerfilRequestInput = ProfileRequestInput
PerfilResponseOutput = ProfileAIOutput
MatchingResponseOutput = MatchingAIOutput
