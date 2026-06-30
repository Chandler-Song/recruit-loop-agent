from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.pipeline import PipelineService
from app.repositories.pipeline import PipelineRepository
from app.schemas.pipeline import PipelineCreate, PipelineUpdate, Pipeline
from typing import List
import uuid

router = APIRouter()

@router.post("", response_model=Pipeline)
async def create_pipeline(pipeline: PipelineCreate, db: AsyncSession = Depends(get_db)):
    repo = PipelineRepository(db)
    service = PipelineService(repo)
    return await service.create_pipeline(pipeline)

@router.get("", response_model=List[Pipeline])
async def get_pipelines(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = PipelineRepository(db)
    service = PipelineService(repo)
    return await service.get_all_pipelines(skip=skip, limit=limit)

@router.get("/{pipeline_id}", response_model=Pipeline)
async def get_pipeline_by_id(pipeline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PipelineRepository(db)
    service = PipelineService(repo)
    try:
        return await service.get_pipeline_by_id(pipeline_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{pipeline_id}", response_model=Pipeline)
async def update_pipeline(pipeline_id: uuid.UUID, pipeline_update: PipelineUpdate, db: AsyncSession = Depends(get_db)):
    repo = PipelineRepository(db)
    service = PipelineService(repo)
    updated_pipeline = await service.update_pipeline(pipeline_id, pipeline_update)
    if not updated_pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return updated_pipeline

@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PipelineRepository(db)
    service = PipelineService(repo)
    success = await service.delete_pipeline(pipeline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"message": "Pipeline deleted successfully"}

@router.put("/{pipeline_id}/status", response_model=Pipeline)
async def update_pipeline_status(pipeline_id: uuid.UUID, status: str, db: AsyncSession = Depends(get_db)):
    repo = PipelineRepository(db)
    service = PipelineService(repo)
    pipeline = await service.update_pipeline_status(pipeline_id, status)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline