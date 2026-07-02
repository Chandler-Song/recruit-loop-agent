from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from typing import List, Optional
import json
import uuid


def _serialize_candidate_data(data: dict) -> dict:
    """Serialize list fields to JSON strings for database storage."""
    for field in ("skills", "search_keywords"):
        if field in data and data[field] is not None:
            data[field] = json.dumps(data[field])
    return data

class CandidateRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, candidate_data: CandidateCreate) -> Candidate:
        data = _serialize_candidate_data(candidate_data.model_dump())
        db_candidate = Candidate(**data)
        self.db_session.add(db_candidate)
        await self.db_session.commit()
        await self.db_session.refresh(db_candidate)
        return db_candidate

    async def get_by_id(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        stmt = select(Candidate).where(Candidate.id == str(candidate_id))
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_source_id(self, source: str, source_id: str) -> Optional[Candidate]:
        stmt = select(Candidate).where(
            (Candidate.source == source) & (Candidate.source_id == source_id)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100, keyword: Optional[str] = None) -> List[Candidate]:
        stmt = select(Candidate)
        if keyword:
            # Search in name, company, title, location, skills
            stmt = stmt.where(
                (Candidate.name.contains(keyword)) |
                (Candidate.company.contains(keyword)) |
                (Candidate.title.contains(keyword)) |
                (Candidate.location.contains(keyword))
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, candidate_id: uuid.UUID, candidate_data: CandidateUpdate) -> Optional[Candidate]:
        db_candidate = await self.get_by_id(candidate_id)
        if db_candidate:
            update_data = _serialize_candidate_data(candidate_data.model_dump(exclude_unset=True))
            for field, value in update_data.items():
                setattr(db_candidate, field, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_candidate)
        return db_candidate

    async def delete(self, candidate_id: uuid.UUID) -> bool:
        db_candidate = await self.get_by_id(candidate_id)
        if db_candidate:
            await self.db_session.delete(db_candidate)
            await self.db_session.commit()
            return True
        return False

    async def increment_appearance_count(self, source: str, source_id: str) -> Optional[Candidate]:
        db_candidate = await self.get_by_source_id(source, source_id)
        if db_candidate:
            db_candidate.appearance_count += 1
            # Update source weight based on appearance count
            if db_candidate.appearance_count <= 2:
                db_candidate.source_weight = float(db_candidate.appearance_count)
            else:
                db_candidate.source_weight = 2.0  # Max weight is 2.0
            await self.db_session.commit()
            await self.db_session.refresh(db_candidate)
        return db_candidate