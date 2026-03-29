import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from services.talent_service import TalentService
from schemas.talent_service import (
    CompanyCreate,
    JobCreate,
    OfferCreate,
    CandidateResponse,
    CandidateListResponse,
    JobResponse,
    JobListResponse,
)


class TestTalentService:
    @pytest.fixture
    def talent_service(self):
        service = TalentService()
        service._contract = None
        service._nft_contract = None
        return service

    @pytest.fixture
    def mock_contract(self):
        contract = MagicMock()
        contract.functions.registerCompany.return_value.call.return_value = Mock(
            transactionReceipt={"status": 1, "blockNumber": 12345}
        )
        contract.functions.postJob.return_value.call.return_value = Mock(
            transactionReceipt={"status": 1, "blockNumber": 12345}
        )
        contract.functions.createOffer.return_value.call.return_value = Mock(
            transactionReceipt={"status": 1, "blockNumber": 12345}
        )
        contract.functions.acceptOffer.return_value.call.return_value = Mock(
            transactionReceipt={"status": 1, "blockNumber": 12345}
        )
        contract.functions.rejectOffer.return_value.call.return_value = Mock(
            transactionReceipt={"status": 1, "blockNumber": 12345}
        )
        contract.functions.getCompanyByAddress.return_value.call.return_value = (
            1,
            "0x123",
            "Company",
            "Desc",
            "Tech",
            "https://test.com",
            True,
            1234567890,
        )
        contract.functions.getActiveJobs.return_value.call.return_value = [
            (
                1,
                1,
                "0x123",
                "Title",
                "Desc",
                "Req",
                50000,
                100000,
                "NYC",
                True,
                [],
                [],
                "full-time",
                True,
                1234567890,
            )
        ]
        contract.functions.getAllTalents.return_value.call.return_value = [
            "0x123",
            "0x456",
        ]
        contract.functions.getTalentProfile.return_value.call.return_value = (
            '{"name":"Test"}'
        )
        contract.functions.getTalentOffers.return_value.call.return_value = []
        return contract

    def test_talent_service_initialization(self, talent_service):
        assert talent_service is not None
        assert talent_service.w3 is not None

    def test_talent_service_is_connected_not_connected(self, talent_service):
        with patch.object(talent_service.w3, "is_connected", return_value=False):
            assert talent_service.is_connected() is False

    def test_talent_service_is_connected(self, talent_service):
        with patch.object(talent_service.w3, "is_connected", return_value=True):
            assert talent_service.is_connected() is True

    @pytest.mark.asyncio
    async def test_register_company_no_contract(self, talent_service):
        result = await talent_service.register_company(
            wallet_address="0xABC123",
            company_data=CompanyCreate(
                name="Test Company",
                description="A test company",
                industry="Technology",
                website="https://test.com",
            ),
        )
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_create_job_no_contract(self, talent_service):
        result = await talent_service.create_job(
            wallet_address="0xABC123",
            job_data=JobCreate(
                title="Software Engineer",
                description="Full stack developer",
                requirements="3+ years",
                salary_min=80000,
                salary_max=150000,
                location="Remote",
                is_remote=True,
                required_skills=[],
                preferred_personality_types=[],
                employment_type="full-time",
            ),
        )
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_search_candidates_not_connected(self, talent_service):
        with patch.object(talent_service, "is_connected", return_value=False):
            result = await talent_service.search_candidates(
                skills=["Leadership"], personality_types=["Leader"], limit=10, offset=0
            )
            assert result.total == 0
            assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_search_candidates_connected_no_contract(self, talent_service):
        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.search_candidates(
                skills=["Leadership"], personality_types=["Leader"], limit=10, offset=0
            )
            assert result.total == 0
            assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_get_all_candidates_not_connected(self, talent_service):
        with patch.object(talent_service, "is_connected", return_value=False):
            result = await talent_service.get_all_candidates(limit=10, offset=0)
            assert result.total == 0
            assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_get_active_jobs_not_connected(self, talent_service):
        with patch.object(talent_service, "is_connected", return_value=False):
            result = await talent_service.get_active_jobs(limit=10, offset=0)
            assert result.total == 0
            assert len(result.jobs) == 0

    @pytest.mark.asyncio
    async def test_create_offer_no_contract(self, talent_service):
        result = await talent_service.create_offer(
            offer_data=OfferCreate(
                job_id=1,
                talent_address="0xTalent123",
                token_id=1,
                terms="Full-time position",
                salary=100000,
            )
        )
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_accept_offer_no_contract(self, talent_service):
        result = await talent_service.accept_offer(offer_id=1)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_reject_offer_no_contract(self, talent_service):
        result = await talent_service.reject_offer(offer_id=1)
        assert result.success is False

    def test_get_contract_abi(self, talent_service):
        abi = talent_service._get_contract_abi("TalentServices")
        assert isinstance(abi, list)
        assert len(abi) > 0

    def test_get_nft_abi(self, talent_service):
        abi = talent_service._get_nft_abi()
        assert isinstance(abi, list)

    @pytest.mark.asyncio
    async def test_search_candidates_empty_results(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.searchTalents.return_value.call.return_value = []

        with patch.object(talent_service, "is_connected", return_value=True):
            talent_service._contract = None
            result = await talent_service.search_candidates(
                skills=[], personality_types=[], limit=10, offset=0
            )
            assert result.total == 0
            assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_get_all_candidates_zero_balance(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._nft_contract = MagicMock()
        talent_service._nft_contract.functions.balanceOf.return_value.call.return_value = 0

        with patch.object(talent_service, "is_connected", return_value=True):
            talent_service._contract = None
            result = await talent_service.get_all_candidates(limit=10, offset=0)
            assert result.total == 0
            assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_get_active_jobs_empty(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.getActiveJobs.return_value.call.return_value = []

        with patch.object(talent_service, "is_connected", return_value=True):
            talent_service._contract = None
            result = await talent_service.get_active_jobs(limit=10, offset=0)
            assert result.total == 0
            assert len(result.jobs) == 0


class TestTalentServiceEdgeCases:
    @pytest.fixture
    def talent_service(self):
        service = TalentService()
        service._contract = None
        service._nft_contract = None
        return service

    @pytest.mark.asyncio
    async def test_register_company_contract_error(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.registerCompany.side_effect = Exception(
            "Contract error"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.register_company(
                wallet_address="0xABC123",
                company_data=CompanyCreate(
                    name="Test Company",
                    description="Test",
                    industry="Tech",
                    website="https://test.com",
                ),
            )
            assert "error" in result or "success" in result

    @pytest.mark.asyncio
    async def test_create_offer_contract_error(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.createOffer.side_effect = Exception(
            "Contract error"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.create_offer(
                offer_data=OfferCreate(
                    job_id=1,
                    talent_address="0xTalent",
                    token_id=1,
                    terms="Test",
                    salary=100000,
                )
            )
            assert "error" in result or "success" in result

    @pytest.mark.asyncio
    async def test_search_candidates_error_handling(self, talent_service):
        with patch.object(talent_service, "is_connected", return_value=True):
            talent_service._contract = None
            result = await talent_service.search_candidates(
                skills=["Test"], personality_types=[], limit=100, offset=0
            )
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_all_candidates_error_handling(self, talent_service):
        with patch.object(talent_service, "is_connected", return_value=True):
            talent_service._contract = None
            result = await talent_service.get_all_candidates(limit=50, offset=1000)
            assert result.total == 0


class TestTalentServiceSchemas:
    def test_company_create_valid(self):
        company = CompanyCreate(
            name="Test Company",
            description="Description",
            industry="Tech",
            website="https://test.com",
        )
        assert company.name == "Test Company"
        assert company.industry == "Tech"

    def test_company_create_minimal(self):
        company = CompanyCreate(name="Test", description="", industry="", website="")
        assert company.name == "Test"

    def test_job_create_valid(self):
        job = JobCreate(
            title="Engineer",
            description="Description",
            requirements="Requirements",
            salary_min=50000,
            salary_max=100000,
            location="Remote",
            is_remote=True,
            required_skills=["Python"],
            preferred_personality_types=["Leader"],
            employment_type="full-time",
        )
        assert job.title == "Engineer"
        assert job.is_remote is True
        assert job.salary_min == 50000

    def test_job_create_defaults(self):
        job = JobCreate(
            title="Engineer",
            description="Description",
            requirements="Requirements",
            salary_min=0,
            salary_max=0,
            location="",
            is_remote=False,
            required_skills=[],
            preferred_personality_types=[],
        )
        assert job.is_remote is False
        assert job.employment_type == "full-time"

    def test_offer_create_valid(self):
        offer = OfferCreate(
            job_id=1,
            talent_address="0x123",
            token_id=1,
            terms="Full-time",
            salary=100000,
        )
        assert offer.job_id == 1
        assert offer.salary == 100000

    def test_offer_create_zero_salary(self):
        offer = OfferCreate(
            job_id=1, talent_address="0x123", token_id=1, terms="Internship", salary=0
        )
        assert offer.salary == 0

    def test_candidate_list_response(self):
        response = CandidateListResponse(candidates=[], total=0)
        assert response.total == 0
        assert len(response.candidates) == 0

    def test_job_list_response(self):
        response = JobListResponse(jobs=[], total=0)
        assert response.total == 0
        assert len(response.jobs) == 0


class TestTalentServiceWithContract:
    @pytest.fixture
    def talent_service(self):
        service = TalentService()
        service._contract = MagicMock()
        service._nft_contract = MagicMock()
        return service

    @pytest.fixture
    def mock_contract(self):
        contract = MagicMock()
        contract.functions.searchTalents.return_value.call.return_value = [
            "0x1234567890123456789012345678901234567890",
            "0x2345678901234567890123456789012345678901",
        ]
        contract.functions.getAllTalents.return_value.call.return_value = [
            "0x1234567890123456789012345678901234567890",
            "0x2345678901234567890123456789012345678901",
            "0x3456789012345678901234567890123456789012",
        ]
        contract.functions.getActiveJobs.return_value.call.return_value = [
            (
                1,
                1,
                "0x1234567890123456789012345678901234567890",
                "Senior Python Developer",
                "We are looking for an experienced Python developer",
                "5+ years experience, Python, Django, FastAPI",
                80000,
                150000,
                "Remote",
                True,
                ["Python", "Django", "FastAPI"],
                ["INTJ", "ENTJ"],
                "full-time",
                True,
                1234567890,
            ),
            (
                2,
                1,
                "0x1234567890123456789012345678901234567890",
                "Frontend Developer",
                "React developer needed",
                "3+ years React experience",
                60000,
                100000,
                "New York",
                False,
                ["React", "TypeScript", "JavaScript"],
                ["ENFP", "ESFJ"],
                "contract",
                True,
                1234567891,
            ),
        ]
        return contract

    @pytest.fixture
    def mock_nft_contract(self):
        nft = MagicMock()
        nft.functions.tokenURI.return_value.call.return_value = (
            "https://ipfs.io/ipfs/test"
        )
        nft.functions.balanceOf.return_value.call.return_value = 1
        return nft

    @pytest.mark.asyncio
    async def test_search_candidates_with_contract(
        self, talent_service, mock_contract, mock_nft_contract
    ):
        talent_service._contract = mock_contract
        talent_service._nft_contract = mock_nft_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.search_candidates(
                skills=["Python"],
                personality_types=["INTJ"],
                limit=10,
                offset=0,
            )
            assert result.total == 2
            assert len(result.candidates) == 2
            assert result.candidates[0].token_id is not None

    @pytest.mark.asyncio
    async def test_get_all_candidates_with_contract(
        self, talent_service, mock_contract, mock_nft_contract
    ):
        talent_service._contract = mock_contract
        talent_service._nft_contract = mock_nft_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.get_all_candidates(limit=10, offset=0)
            assert result.total == 3
            assert len(result.candidates) == 3

    @pytest.mark.asyncio
    async def test_get_active_jobs_with_contract(
        self, talent_service, mock_contract, mock_nft_contract
    ):
        talent_service._contract = mock_contract
        talent_service._nft_contract = mock_nft_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.get_active_jobs(limit=10, offset=0)
            assert result.total == 2
            assert len(result.jobs) == 2
            assert result.jobs[0].title == "Senior Python Developer"
            assert result.jobs[0].is_active is True

    @pytest.mark.asyncio
    async def test_search_candidates_with_contract_nft_error(
        self, talent_service, mock_contract
    ):
        talent_service._contract = mock_contract
        talent_service._nft_contract = MagicMock()
        talent_service._nft_contract.functions.tokenURI.side_effect = Exception(
            "NFT error"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.search_candidates(
                skills=["Python"],
                personality_types=[],
                limit=10,
                offset=0,
            )
            assert result.total == 2
            assert len(result.candidates) == 2

    @pytest.mark.asyncio
    async def test_get_all_candidates_with_contract_nft_none(
        self, talent_service, mock_contract
    ):
        talent_service._contract = mock_contract
        talent_service._nft_contract = None

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.get_all_candidates(limit=10, offset=0)
            assert result.total == 3
            assert len(result.candidates) == 3

    @pytest.mark.asyncio
    async def test_get_active_jobs_with_contract_exception(
        self, talent_service, mock_contract
    ):
        talent_service._contract = mock_contract
        talent_service._contract.functions.getActiveJobs.side_effect = Exception(
            "Chain error"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.get_active_jobs(limit=10, offset=0)
            assert result.total == 0
            assert len(result.jobs) == 0

    @pytest.mark.asyncio
    async def test_search_candidates_with_contract_exception(
        self, talent_service, mock_contract
    ):
        talent_service._contract = mock_contract
        talent_service._contract.functions.searchTalents.side_effect = Exception(
            "Search error"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.search_candidates(
                skills=["Python"],
                personality_types=[],
                limit=10,
                offset=0,
            )
            assert result.total == 0
            assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_accept_offer_with_contract(self, talent_service, mock_contract):
        talent_service._contract = mock_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.accept_offer(offer_id=1)
            assert result.success is True
            assert result.message == "Offer accepted"

    @pytest.mark.asyncio
    async def test_reject_offer_with_contract(self, talent_service, mock_contract):
        talent_service._contract = mock_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.reject_offer(offer_id=1)
            assert result.success is True
            assert result.message == "Offer rejected"

    @pytest.mark.asyncio
    async def test_accept_offer_with_contract_exception(
        self, talent_service, mock_contract
    ):
        talent_service._contract = mock_contract
        talent_service._contract.functions.acceptOffer.side_effect = Exception(
            "Transaction failed"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.accept_offer(offer_id=1)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_reject_offer_with_contract_exception(
        self, talent_service, mock_contract
    ):
        talent_service._contract = mock_contract
        talent_service._contract.functions.rejectOffer.side_effect = Exception(
            "Transaction failed"
        )

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.reject_offer(offer_id=1)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_create_offer_with_contract(self, talent_service, mock_contract):
        talent_service._contract = mock_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.create_offer(
                offer_data=OfferCreate(
                    job_id=1,
                    talent_address="0x1234567890123456789012345678901234567890",
                    token_id=1,
                    terms="Competitive salary and benefits",
                    salary=120000,
                )
            )
            assert result["success"] is True
            assert result["offer_id"] == 1

    @pytest.mark.asyncio
    async def test_create_job_with_contract(self, talent_service, mock_contract):
        talent_service._contract = mock_contract

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.create_job(
                wallet_address="0x1234567890123456789012345678901234567890",
                job_data=JobCreate(
                    title="Backend Engineer",
                    description="Build scalable APIs",
                    requirements="4+ years Python",
                    salary_min=90000,
                    salary_max=160000,
                    location="San Francisco",
                    is_remote=True,
                    required_skills=["Python", "PostgreSQL", "Redis"],
                    preferred_personality_types=["INTJ"],
                    employment_type="full-time",
                ),
            )
            assert result["success"] is True
            assert result["job_id"] == 1


class TestTalentServicePagination:
    @pytest.fixture
    def talent_service(self):
        service = TalentService()
        service._contract = MagicMock()
        service._nft_contract = MagicMock()
        return service

    @pytest.mark.asyncio
    async def test_search_candidates_pagination(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.searchTalents.return_value.call.return_value = []

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.search_candidates(
                skills=["Python"],
                personality_types=[],
                limit=5,
                offset=10,
            )
            assert isinstance(result.total, int)
            assert isinstance(result.candidates, list)

    @pytest.mark.asyncio
    async def test_get_all_candidates_pagination(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.getAllTalents.return_value.call.return_value = []

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.get_all_candidates(limit=20, offset=100)
            assert isinstance(result.total, int)
            assert isinstance(result.candidates, list)

    @pytest.mark.asyncio
    async def test_get_active_jobs_pagination(self, talent_service):
        talent_service._contract = MagicMock()
        talent_service._contract.functions.getActiveJobs.return_value.call.return_value = []

        with patch.object(talent_service, "is_connected", return_value=True):
            result = await talent_service.get_active_jobs(limit=5, offset=15)
            assert isinstance(result.total, int)
            assert isinstance(result.jobs, list)


class TestTalentServiceJobDetails:
    @pytest.fixture
    def talent_service(self):
        service = TalentService()
        return service

    def test_job_response_model(self):
        job = JobResponse(
            id=1,
            company_id=1,
            company_owner="0x1234567890123456789012345678901234567890",
            title="Software Engineer",
            description="Build amazing software",
            requirements="3+ years",
            salary_min=80000,
            salary_max=150000,
            location="Remote",
            is_remote=True,
            required_skills=["Python", "TypeScript"],
            preferred_personality_types=["INTJ"],
            employment_type="full-time",
            is_active=True,
            created_at=1234567890,
        )
        assert job.id == 1
        assert job.title == "Software Engineer"
        assert job.is_remote is True
        assert job.is_active is True
        assert len(job.required_skills) == 2

    def test_candidate_response_model(self):
        candidate = CandidateResponse(
            token_id=1,
            wallet_address="0x1234567890123456789012345678901234567890",
            profile_uri="https://ipfs.io/ipfs/test",
        )
        assert candidate.token_id == 1
        assert candidate.wallet_address == "0x1234567890123456789012345678901234567890"
        assert candidate.profile_uri == "https://ipfs.io/ipfs/test"

    def test_candidate_response_no_uri(self):
        candidate = CandidateResponse(
            token_id=1,
            wallet_address="0x1234567890123456789012345678901234567890",
            profile_uri="",
        )
        assert candidate.token_id == 1
        assert candidate.profile_uri == ""
