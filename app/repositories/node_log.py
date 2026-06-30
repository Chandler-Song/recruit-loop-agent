from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.node_log import NodeLog
from app.schemas.node_log import NodeLogCreate, NodeLogUpdate
from typing import List, Optional
import uuid
from datetime import datetime

class NodeLogRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, node_log_data: NodeLogCreate) -> NodeLog:
        db_node_log = NodeLog(**node_log_data.model_dump())
        self.db_session.add(db_node_log)
        await self.db_session.commit()
        await self.db_session.refresh(db_node_log)
        return db_node_log

    async def get_by_id(self, node_log_id: uuid.UUID) -> Optional[NodeLog]:
        stmt = select(NodeLog).where(NodeLog.id == node_log_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_run(self, run_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[NodeLog]:
        stmt = select(NodeLog).where(NodeLog.run_id == run_id).order_by(NodeLog.started_at.desc()).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_by_node_name(self, run_id: uuid.UUID, node_name: str) -> List[NodeLog]:
        stmt = select(NodeLog).where(
            (NodeLog.run_id == run_id) & (NodeLog.node_name == node_name)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[NodeLog]:
        stmt = select(NodeLog).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, node_log_id: uuid.UUID, node_log_data: NodeLogUpdate) -> Optional[NodeLog]:
        db_node_log = await self.get_by_id(node_log_id)
        if db_node_log:
            for field, value in node_log_data.model_dump(exclude_unset=True).items():
                setattr(db_node_log, field, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_node_log)
        return db_node_log

    async def delete(self, node_log_id: uuid.UUID) -> bool:
        db_node_log = await self.get_by_id(node_log_id)
        if db_node_log:
            await self.db_session.delete(db_node_log)
            await self.db_session.commit()
            return True
        return False