from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.candidate import CandidateService
from app.repositories.candidate import CandidateRepository
from app.schemas.candidate import CandidateCreate, CandidateUpdate, Candidate
from typing import List
import uuid

router = APIRouter()

@router.post("", response_model=Candidate)
async def create_candidate(candidate: CandidateCreate, db: AsyncSession = Depends(get_db)):
    repo = CandidateRepository(db)
    service = CandidateService(repo)
    return await service.create_candidate(candidate)

@router.get("", response_model=List[Candidate])
async def get_candidates(skip: int = 0, limit: int = 100, keyword: str = None, db: AsyncSession = Depends(get_db)):
    repo = CandidateRepository(db)
    service = CandidateService(repo)
    return await service.get_all_candidates(skip=skip, limit=limit, keyword=keyword)

@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = CandidateRepository(db)
    service = CandidateService(repo)
    try:
        return await service.get_candidate_by_id(candidate_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{candidate_id}", response_model=Candidate)
async def update_candidate(candidate_id: uuid.UUID, candidate_update: CandidateUpdate, db: AsyncSession = Depends(get_db)):
    repo = CandidateRepository(db)
    service = CandidateService(repo)
    updated_candidate = await service.update_candidate(candidate_id, candidate_update)
    if not updated_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return updated_candidate

@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = CandidateRepository(db)
    service = CandidateService(repo)
    success = await service.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Candidate deleted successfully"}