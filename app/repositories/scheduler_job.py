from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.scheduler_job import SchedulerJob
from app.schemas.scheduler_job import SchedulerJobCreate, SchedulerJobUpdate
from typing import List, Optional
import uuid
from datetime import datetime

class SchedulerJobRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, job_data: dict) -> SchedulerJob:
        db_job = SchedulerJob(**job_data)
        self.db_session.add(db_job)
        await self.db_session.commit()
        await self.db_session.refresh(db_job)
        return db_job

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[SchedulerJob]:
        stmt = select(SchedulerJob).where(SchedulerJob.id == job_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_position_id(self, position_id: uuid.UUID) -> Optional[SchedulerJob]:
        stmt = select(SchedulerJob).where(SchedulerJob.position_id == position_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[SchedulerJob]:
        stmt = select(SchedulerJob).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, job_id: uuid.UUID, job_data: dict) -> Optional[SchedulerJob]:
        db_job = await self.get_by_id(job_id)
        if db_job:
            for field, value in job_data.items():
                setattr(db_job, field, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_job)
        return db_job

    async def update_status(self, position_id: uuid.UUID, status: str) -> Optional[SchedulerJob]:
        db_job = await self.get_by_position_id(position_id)
        if db_job:
            db_job.status = status
            await self.db_session.commit()
            await self.db_session.refresh(db_job)
        return db_job

    async def update_last_run(self, position_id: uuid.UUID, last_run: datetime) -> Optional[SchedulerJob]:
        db_job = await self.get_by_position_id(position_id)
        if db_job:
            db_job.last_run = last_run
            await self.db_session.commit()
            await self.db_session.refresh(db_job)
        return db_job

    async def increment_run_count(self, position_id: uuid.UUID) -> Optional[SchedulerJob]:
        db_job = await self.get_by_position_id(position_id)
        if db_job:
            db_job.total_runs += 1
            await self.db_session.commit()
            await self.db_session.refresh(db_job)
        return db_job

    async def delete(self, job_id: uuid.UUID) -> bool:
        db_job = await self.get_by_id(job_id)
        if db_job:
            await self.db_session.delete(db_job)
            await self.db_session.commit()
            return True
        return False