from typing import List, Optional, Dict, Any
from datetime import datetime
from web3 import Web3
from config.settings import get_settings
from schemas.talent_service import (
    CompanyCreate,
    CompanyResponse,
    JobCreate,
    JobResponse,
    JobListResponse,
    CandidateResponse,
    CandidateListResponse,
    OfferCreate,
    OfferResponse,
    OfferActionResponse,
    OfferListResponse,
)
from core import get_logger

logger = get_logger()
settings = get_settings()


class TalentService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.blockchain_rpc_url))
        self.contract_address = settings.talent_services_contract_address
        self.nft_address = settings.talent_nft_contract_address
        self._contract = None
        self._nft_contract = None

    @property
    def contract(self):
        if not self._contract and self.contract_address:
            try:
                abi = self._get_contract_abi("TalentServices")
                self._contract = self.w3.eth.contract(
                    address=self.contract_address, abi=abi
                )
            except Exception as e:
                logger.error(f"Error loading TalentServices contract: {e}")
        return self._contract

    @property
    def nft_contract(self):
        if not self._nft_contract and self.nft_address:
            try:
                abi = self._get_nft_abi()
                self._nft_contract = self.w3.eth.contract(
                    address=self.nft_address, abi=abi
                )
            except Exception as e:
                logger.error(f"Error loading TalentNFT contract: {e}")
        return self._nft_contract

    def _get_contract_abi(self, contract_name: str) -> List[Dict]:
        # Simplified ABI - in production, load from compiled contract
        return [
            {
                "inputs": [
                    {"name": "_name", "type": "string"},
                    {"name": "_description", "type": "string"},
                    {"name": "_industry", "type": "string"},
                    {"name": "_website", "type": "string"},
                ],
                "name": "registerCompany",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "_companyId", "type": "uint256"},
                    {"name": "_name", "type": "string"},
                    {"name": "_description", "type": "string"},
                    {"name": "_industry", "type": "string"},
                    {"name": "_website", "type": "string"},
                ],
                "name": "updateCompany",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "getCompanyByAddress",
                "outputs": [
                    {
                        "components": [
                            {"name": "id", "type": "uint256"},
                            {"name": "owner", "type": "address"},
                            {"name": "name", "type": "string"},
                            {"name": "description", "type": "string"},
                            {"name": "industry", "type": "string"},
                            {"name": "website", "type": "string"},
                            {"name": "isActive", "type": "bool"},
                            {"name": "createdAt", "type": "uint256"},
                        ],
                        "name": "",
                        "type": "tuple",
                    }
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "_title", "type": "string"},
                    {"name": "_description", "type": "string"},
                    {"name": "_requirements", "type": "string"},
                    {"name": "_salaryMin", "type": "uint256"},
                    {"name": "_salaryMax", "type": "uint256"},
                    {"name": "_location", "type": "string"},
                    {"name": "_isRemote", "type": "bool"},
                    {"name": "_requiredSkills", "type": "string[]"},
                    {"name": "_preferredPersonalityTypes", "type": "string[]"},
                    {"name": "_employmentType", "type": "string"},
                ],
                "name": "postJob",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "_skill", "type": "string"},
                    {"name": "_personalityType", "type": "string"},
                    {"name": "_limit", "type": "uint256"},
                    {"name": "_offset", "type": "uint256"},
                ],
                "name": "searchTalents",
                "outputs": [{"name": "", "type": "address[]"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "_limit", "type": "uint256"},
                    {"name": "_offset", "type": "uint256"},
                ],
                "name": "getAllTalents",
                "outputs": [{"name": "", "type": "address[]"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [{"name": "_tokenId", "type": "uint256"}],
                "name": "getTalentProfile",
                "outputs": [{"name": "", "type": "string"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "_jobId", "type": "uint256"},
                    {"name": "_talentAddress", "type": "address"},
                    {"name": "_tokenId", "type": "uint256"},
                    {"name": "_terms", "type": "string"},
                    {"name": "_salary", "type": "uint256"},
                ],
                "name": "createOffer",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"name": "_offerId", "type": "uint256"}],
                "name": "acceptOffer",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"name": "_offerId", "type": "uint256"}],
                "name": "rejectOffer",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"name": "_talent", "type": "address"}],
                "name": "getTalentOffers",
                "outputs": [
                    {
                        "components": [
                            {"name": "id", "type": "uint256"},
                            {"name": "jobId", "type": "uint256"},
                            {"name": "company", "type": "address"},
                            {"name": "talentAddress", "type": "address"},
                            {"name": "tokenId", "type": "uint256"},
                            {"name": "terms", "type": "string"},
                            {"name": "salary", "type": "uint256"},
                            {"name": "status", "type": "uint256"},
                            {"name": "createdAt", "type": "uint256"},
                            {"name": "respondedAt", "type": "uint256"},
                        ],
                        "name": "",
                        "type": "tuple[]",
                    }
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "_limit", "type": "uint256"},
                    {"name": "_offset", "type": "uint256"},
                ],
                "name": "getActiveJobs",
                "outputs": [
                    {
                        "components": [
                            {"name": "id", "type": "uint256"},
                            {"name": "companyId", "type": "uint256"},
                            {"name": "companyOwner", "type": "address"},
                            {"name": "title", "type": "string"},
                            {"name": "description", "type": "string"},
                            {"name": "requirements", "type": "string"},
                            {"name": "salaryMin", "type": "uint256"},
                            {"name": "salaryMax", "type": "uint256"},
                            {"name": "location", "type": "string"},
                            {"name": "isRemote", "type": "bool"},
                            {"name": "requiredSkills", "type": "string[]"},
                            {"name": "preferredPersonalityTypes", "type": "string[]"},
                            {"name": "employmentType", "type": "string"},
                            {"name": "isActive", "type": "bool"},
                            {"name": "createdAt", "type": "uint256"},
                        ],
                        "name": "",
                        "type": "tuple[]",
                    }
                ],
                "stateMutability": "view",
                "type": "function",
            },
        ]

    def _get_nft_abi(self) -> List[Dict]:
        return [
            {
                "inputs": [{"name": "owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "index", "type": "uint256"},
                ],
                "name": "tokenOfOwnerByIndex",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "tokenURI",
                "outputs": [{"name": "", "type": "string"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "getProfileDataHash",
                "outputs": [{"name": "", "type": "bytes32"}],
                "stateMutability": "view",
                "type": "function",
            },
        ]

    def is_connected(self) -> bool:
        return self.w3.is_connected()

    async def register_company(
        self, wallet_address: str, company_data: CompanyCreate
    ) -> Dict[str, Any]:
        if not self.contract:
            return {"success": False, "error": "Contract not configured"}

        try:
            # In production, this would be a transaction
            # For now, return mock success
            return {
                "success": True,
                "company_id": 1,
                "message": "Company registered successfully",
            }
        except Exception as e:
            logger.error(f"Error registering company: {e}")
            return {"success": False, "error": str(e)}

    async def search_candidates(
        self,
        skills: Optional[List[str]] = None,
        personality_types: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> CandidateListResponse:
        if not self.is_connected():
            # Return empty response if not connected to blockchain
            return CandidateListResponse(candidates=[], total=0)

        try:
            skill = skills[0] if skills else ""
            personality = personality_types[0] if personality_types else ""

            if self.contract:
                talents = self.contract.functions.searchTalents(
                    skill, personality, limit, offset
                ).call()

                candidates = []
                for addr in talents:
                    token_id = int(addr, 0) if isinstance(addr, str) else addr
                    profile_uri = ""
                    if self.nft_contract:
                        try:
                            profile_uri = self.nft_contract.functions.tokenURI(
                                token_id
                            ).call()
                        except:
                            pass

                    candidates.append(
                        CandidateResponse(
                            token_id=token_id,
                            wallet_address=addr,
                            profile_uri=profile_uri,
                        )
                    )

                return CandidateListResponse(
                    candidates=candidates, total=len(candidates)
                )

            return CandidateListResponse(candidates=[], total=0)
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            return CandidateListResponse(candidates=[], total=0)

    async def get_all_candidates(
        self, limit: int = 20, offset: int = 0
    ) -> CandidateListResponse:
        if not self.is_connected():
            return CandidateListResponse(candidates=[], total=0)

        try:
            if self.contract:
                talents = self.contract.functions.getAllTalents(limit, offset).call()

                candidates = []
                for addr in talents:
                    token_id = int(addr, 0) if isinstance(addr, str) else addr
                    profile_uri = ""
                    if self.nft_contract:
                        try:
                            profile_uri = self.nft_contract.functions.tokenURI(
                                token_id
                            ).call()
                        except:
                            pass

                    candidates.append(
                        CandidateResponse(
                            token_id=token_id,
                            wallet_address=addr,
                            profile_uri=profile_uri,
                        )
                    )

                return CandidateListResponse(
                    candidates=candidates, total=len(candidates)
                )

            return CandidateListResponse(candidates=[], total=0)
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return CandidateListResponse(candidates=[], total=0)

    async def get_active_jobs(
        self, limit: int = 20, offset: int = 0
    ) -> JobListResponse:
        """Get all active job postings"""
        if not self.is_connected():
            return JobListResponse(jobs=[], total=0)

        try:
            if self.contract:
                jobs_data = self.contract.functions.getActiveJobs(limit, offset).call()
                jobs = []
                for job_data in jobs_data:
                    jobs.append(
                        JobResponse(
                            id=job_data[0],
                            company_id=job_data[1],
                            company_owner=job_data[2],
                            title=job_data[3],
                            description=job_data[4],
                            requirements=job_data[5],
                            salary_min=job_data[6],
                            salary_max=job_data[7],
                            location=job_data[8],
                            is_remote=job_data[9],
                            required_skills=job_data[10],
                            preferred_personality_types=job_data[11],
                            employment_type=job_data[12],
                            is_active=job_data[13],
                            created_at=job_data[14],
                        )
                    )
                return JobListResponse(jobs=jobs, total=len(jobs))
            return JobListResponse(jobs=[], total=0)
        except Exception as e:
            logger.error(f"Error getting active jobs: {e}")
            return JobListResponse(jobs=[], total=0)

    async def create_job(
        self, wallet_address: str, job_data: JobCreate
    ) -> Dict[str, Any]:
        """Create a new job posting"""
        if not self.contract:
            return {"success": False, "error": "Contract not configured"}

        try:
            return {
                "success": True,
                "job_id": 1,
                "message": "Job created successfully",
            }
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return {"success": False, "error": str(e)}

    async def create_offer(self, offer_data: OfferCreate) -> Dict[str, Any]:
        if not self.contract:
            return {"success": False, "error": "Contract not configured"}

        try:
            # In production, this would be a transaction
            return {
                "success": True,
                "offer_id": 1,
                "message": "Offer created successfully",
            }
        except Exception as e:
            logger.error(f"Error creating offer: {e}")
            return {"success": False, "error": str(e)}

    async def accept_offer(self, offer_id: int) -> OfferActionResponse:
        if not self.contract:
            return OfferActionResponse(
                success=False,
                message="Contract not configured",
                offer=OfferResponse(
                    id=offer_id,
                    job_id=0,
                    company="",
                    talent_address="",
                    token_id=0,
                    terms="",
                    salary=0,
                    status=0,
                    created_at=None,
                ),
            )

        try:
            return OfferActionResponse(
                success=True,
                message="Offer accepted",
                offer=OfferResponse(
                    id=offer_id,
                    job_id=0,
                    company="",
                    talent_address="",
                    token_id=0,
                    terms="",
                    salary=0,
                    status=1,
                    created_at=None,
                ),
            )
        except Exception as e:
            logger.error(f"Error accepting offer: {e}")
            return OfferActionResponse(
                success=False,
                message=str(e),
                offer=OfferResponse(
                    id=offer_id,
                    job_id=0,
                    company="",
                    talent_address="",
                    token_id=0,
                    terms="",
                    salary=0,
                    status=0,
                    created_at=None,
                ),
            )

    async def reject_offer(self, offer_id: int) -> OfferActionResponse:
        if not self.contract:
            return OfferActionResponse(
                success=False,
                message="Contract not configured",
                offer=OfferResponse(
                    id=offer_id,
                    job_id=0,
                    company="",
                    talent_address="",
                    token_id=0,
                    terms="",
                    salary=0,
                    status=0,
                    created_at=None,
                ),
            )

        try:
            return OfferActionResponse(
                success=True,
                message="Offer rejected",
                offer=OfferResponse(
                    id=offer_id,
                    job_id=0,
                    company="",
                    talent_address="",
                    token_id=0,
                    terms="",
                    salary=0,
                    status=2,
                    created_at=None,
                ),
            )
        except Exception as e:
            logger.error(f"Error rejecting offer: {e}")
            return OfferActionResponse(
                success=False,
                message=str(e),
                offer=OfferResponse(
                    id=offer_id,
                    job_id=0,
                    company="",
                    talent_address="",
                    token_id=0,
                    terms="",
                    salary=0,
                    status=0,
                    created_at=None,
                ),
            )

    async def get_talent_offers(self, talent_address: str) -> OfferListResponse:
        if not self.contract:
            return OfferListResponse(offers=[], total=0)

        try:
            offers_data = self.contract.functions.getTalentOffers(talent_address).call()

            offers = []
            for offer_data in offers_data:
                offers.append(
                    OfferResponse(
                        id=offer_data[0],
                        job_id=offer_data[1],
                        company=offer_data[2],
                        talent_address=offer_data[3],
                        token_id=offer_data[4],
                        terms=offer_data[5],
                        salary=offer_data[6],
                        status=offer_data[7],
                        created_at=datetime.fromtimestamp(offer_data[8])
                        if offer_data[8] > 0
                        else None,
                        responded_at=datetime.fromtimestamp(offer_data[9])
                        if offer_data[9] > 0
                        else None,
                    )
                )

            return OfferListResponse(offers=offers, total=len(offers))
        except Exception as e:
            logger.error(f"Error getting talent offers: {e}")
            return OfferListResponse(offers=[], total=0)


# Singleton instance
talent_service = TalentService()
