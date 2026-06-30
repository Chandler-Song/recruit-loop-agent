from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.outreach_log import OutreachLog
from app.schemas.outreach_log import OutreachLogCreate, OutreachLogUpdate
from typing import List, Optional
import uuid
from datetime import datetime

class OutreachLogRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, outreach_log_data: OutreachLogCreate) -> OutreachLog:
        db_outreach_log = OutreachLog(**outreach_log_data.model_dump())
        self.db_session.add(db_outreach_log)
        await self.db_session.commit()
        await self.db_session.refresh(db_outreach_log)
        return db_outreach_log

    async def get_by_id(self, outreach_log_id: uuid.UUID) -> Optional[OutreachLog]:
        stmt = select(OutreachLog).where(OutreachLog.id == outreach_log_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_pipeline(self, pipeline_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[OutreachLog]:
        stmt = select(OutreachLog).where(OutreachLog.pipeline_id == pipeline_id).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[OutreachLog]:
        stmt = select(OutreachLog).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update_status(self, outreach_log_id: uuid.UUID, status: str) -> Optional[OutreachLog]:
        db_outreach_log = await self.get_by_id(outreach_log_id)
        if db_outreach_log:
            db_outreach_log.status = status
            db_outreach_log.sent_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(db_outreach_log)
        return db_outreach_log

    async def update_status_with_error(self, outreach_log_id: uuid.UUID, status: str, error: str) -> Optional[OutreachLog]:
        db_outreach_log = await self.get_by_id(outreach_log_id)
        if db_outreach_log:
            db_outreach_log.status = status
            db_outreach_log.error = error
            db_outreach_log.sent_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(db_outreach_log)
        return db_outreach_log

    async def delete(self, outreach_log_id: uuid.UUID) -> bool:
        db_outreach_log = await self.get_by_id(outreach_log_id)
        if db_outreach_log:
            await self.db_session.delete(db_outreach_log)
            await self.db_session.commit()
            return True
        return False