from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.agent_run import AgentRun
from app.schemas.agent_run import AgentRunCreate, AgentRunUpdate
from typing import List, Optional
import uuid
from datetime import datetime

class AgentRunRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, agent_run_data: AgentRunCreate) -> AgentRun:
        db_agent_run = AgentRun(**agent_run_data.model_dump())
        self.db_session.add(db_agent_run)
        await self.db_session.commit()
        await self.db_session.refresh(db_agent_run)
        return db_agent_run

    async def get_by_id(self, agent_run_id: uuid.UUID) -> Optional[AgentRun]:
        stmt = select(AgentRun).where(AgentRun.id == agent_run_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_position(self, position_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[AgentRun]:
        stmt = select(AgentRun).where(AgentRun.position_id == position_id).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AgentRun]:
        stmt = select(AgentRun).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, agent_run_id: uuid.UUID, agent_run_data: AgentRunUpdate) -> Optional[AgentRun]:
        db_agent_run = await self.get_by_id(agent_run_id)
        if db_agent_run:
            for field, value in agent_run_data.model_dump(exclude_unset=True).items():
                setattr(db_agent_run, field, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_agent_run)
        return db_agent_run

    async def update_completion(
        self,
        agent_run_id: uuid.UUID,
        status: str,
        duration_ms: int,
        candidates_found: int,
        candidates_added: int,
        emails_sent: int,
        error: str = None
    ) -> Optional[AgentRun]:
        db_agent_run = await self.get_by_id(agent_run_id)
        if db_agent_run:
            db_agent_run.status = status
            db_agent_run.duration_ms = duration_ms
            db_agent_run.finished_at = datetime.utcnow()
            db_agent_run.candidates_found = candidates_found
            db_agent_run.candidates_added = candidates_added
            db_agent_run.emails_sent = emails_sent
            if error:
                db_agent_run.error = error
            await self.db_session.commit()
            await self.db_session.refresh(db_agent_run)
        return db_agent_run

    async def delete(self, agent_run_id: uuid.UUID) -> bool:
        db_agent_run = await self.get_by_id(agent_run_id)
        if db_agent_run:
            await self.db_session.delete(db_agent_run)
            await self.db_session.commit()
            return True
        return False