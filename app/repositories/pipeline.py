from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.pipeline import Pipeline
from app.schemas.pipeline import PipelineCreate, PipelineUpdate
from typing import List, Optional
import uuid

class PipelineRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, pipeline_data: PipelineCreate) -> Pipeline:
        db_pipeline = Pipeline(**pipeline_data.model_dump())
        self.db_session.add(db_pipeline)
        await self.db_session.commit()
        await self.db_session.refresh(db_pipeline)
        return db_pipeline

    async def get_by_id(self, pipeline_id: uuid.UUID) -> Optional[Pipeline]:
        stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_position_and_candidate(self, position_id: uuid.UUID, candidate_id: uuid.UUID) -> Optional[Pipeline]:
        stmt = select(Pipeline).where(
            (Pipeline.position_id == position_id) & (Pipeline.candidate_id == candidate_id)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_position(self, position_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Pipeline]:
        stmt = select(Pipeline).where(Pipeline.position_id == position_id).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(self, position_id: uuid.UUID, status: str) -> List[Pipeline]:
        stmt = select(Pipeline).where(
            (Pipeline.position_id == position_id) & (Pipeline.status == status)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Pipeline]:
        stmt = select(Pipeline).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, pipeline_id: uuid.UUID, pipeline_data: PipelineUpdate) -> Optional[Pipeline]:
        db_pipeline = await self.get_by_id(pipeline_id)
        if db_pipeline:
            for field, value in pipeline_data.model_dump(exclude_unset=True).items():
                setattr(db_pipeline, field, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_pipeline)
        return db_pipeline

    async def update_status(self, pipeline_id: uuid.UUID, status: str) -> Optional[Pipeline]:
        db_pipeline = await self.get_by_id(pipeline_id)
        if db_pipeline:
            db_pipeline.status = status
            await self.db_session.commit()
            await self.db_session.refresh(db_pipeline)
        return db_pipeline

    async def delete(self, pipeline_id: uuid.UUID) -> bool:
        db_pipeline = await self.get_by_id(pipeline_id)
        if db_pipeline:
            await self.db_session.delete(db_pipeline)
            await self.db_session.commit()
            return True
        return False