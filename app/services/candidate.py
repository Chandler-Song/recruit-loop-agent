from typing import List, Optional
from app.repositories.candidate import CandidateRepository
from app.schemas.candidate import CandidateCreate, CandidateUpdate, Candidate
from app.core.exceptions import CandidateNotFoundException
import uuid

class CandidateService:
    def __init__(self, candidate_repo: CandidateRepository):
        self.candidate_repo = candidate_repo

    async def create_candidate(self, candidate_data: CandidateCreate) -> Candidate:
        # Check if candidate already exists by source and source_id
        existing_candidate = await self.candidate_repo.get_by_source_id(
            candidate_data.source, 
            candidate_data.source_id
        )
        
        if existing_candidate:
            # Increment appearance count and return existing candidate
            return await self.candidate_repo.increment_appearance_count(
                candidate_data.source, 
                candidate_data.source_id
            )
        else:
            # Create new candidate
            return await self.candidate_repo.create(candidate_data)

    async def get_candidate_by_id(self, candidate_id: uuid.UUID) -> Candidate:
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise CandidateNotFoundException(f"Candidate with id {candidate_id} not found")
        return candidate

    async def get_candidate_by_source_id(self, source: str, source_id: str) -> Optional[Candidate]:
        return await self.candidate_repo.get_by_source_id(source, source_id)

    async def get_all_candidates(self, skip: int = 0, limit: int = 100, keyword: Optional[str] = None) -> List[Candidate]:
        return await self.candidate_repo.get_all(skip, limit, keyword)

    async def update_candidate(self, candidate_id: uuid.UUID, candidate_data: CandidateUpdate) -> Optional[Candidate]:
        return await self.candidate_repo.update(candidate_id, candidate_data)

    async def delete_candidate(self, candidate_id: uuid.UUID) -> bool:
        return await self.candidate_repo.delete(candidate_id)

    async def deduplicate_candidates(self, source: str, source_ids: List[str]) -> List[Candidate]:
        """
        Find existing candidates and return a list of new candidates to be created
        """
        new_candidates = []
        for source_id in source_ids:
            existing = await self.candidate_repo.get_by_source_id(source, source_id)
            if not existing:
                new_candidates.append(source_id)
            else:
                # Increment appearance count for existing candidate
                await self.candidate_repo.increment_appearance_count(source, source_id)
        return new_candidates