from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.position import PositionService
from app.repositories.position import PositionRepository
from app.schemas.position import PositionCreate, PositionUpdate, Position
from typing import List
import uuid

router = APIRouter()

@router.post("", response_model=Position)
async def create_position(position: PositionCreate, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    return await service.create_position(position)

@router.get("", response_model=List[Position])
async def get_positions(skip: int = 0, limit: int = 100, status: str = None, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    return await service.get_all_positions(skip=skip, limit=limit, status=status)

@router.get("/{position_id}", response_model=Position)
async def get_position(position_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    try:
        return await service.get_position_by_id(position_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{position_id}", response_model=Position)
async def update_position(position_id: uuid.UUID, position_update: PositionUpdate, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    updated_position = await service.update_position(position_id, position_update)
    if not updated_position:
        raise HTTPException(status_code=404, detail="Position not found")
    return updated_position

@router.delete("/{position_id}")
async def delete_position(position_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    success = await service.delete_position(position_id)
    if not success:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"message": "Position deleted successfully"}

@router.post("/{position_id}/pause", response_model=Position)
async def pause_position(position_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    position = await service.pause_position(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.post("/{position_id}/resume", response_model=Position)
async def resume_position(position_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    position = await service.resume_position(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.post("/{position_id}/close", response_model=Position)
async def close_position(position_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PositionRepository(db)
    service = PositionService(repo)
    position = await service.close_position(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position