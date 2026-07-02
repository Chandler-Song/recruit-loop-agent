from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate
from typing import List, Optional
import json
import uuid


def _serialize_position_data(data: dict) -> dict:
    """Serialize list fields to JSON strings for database storage."""
    for field in ("required_skills", "search_keywords"):
        if field in data and data[field] is not None:
            data[field] = json.dumps(data[field])
    return data

class PositionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, position_data: PositionCreate) -> Position:
        data = _serialize_position_data(position_data.model_dump())
        db_position = Position(**data)
        self.db_session.add(db_position)
        await self.db_session.commit()
        await self.db_session.refresh(db_position)
        return db_position

    async def get_by_id(self, position_id: uuid.UUID) -> Optional[Position]:
        stmt = select(Position).where(Position.id == str(position_id))
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Position]:
        stmt = select(Position)
        if status:
            stmt = stmt.where(Position.status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, position_id: uuid.UUID, position_data: PositionUpdate) -> Optional[Position]:
        db_position = await self.get_by_id(position_id)
        if db_position:
            update_data = _serialize_position_data(position_data.model_dump(exclude_unset=True))
            for field, value in update_data.items():
                setattr(db_position, field, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_position)
        return db_position

    async def delete(self, position_id: uuid.UUID) -> bool:
        db_position = await self.get_by_id(position_id)
        if db_position:
            await self.db_session.delete(db_position)
            await self.db_session.commit()
            return True
        return False

    async def update_status(self, position_id: uuid.UUID, status: str) -> Optional[Position]:
        db_position = await self.get_by_id(position_id)
        if db_position:
            db_position.status = status
            db_position.loop_enabled = (status == "active")
            await self.db_session.commit()
            await self.db_session.refresh(db_position)
        return db_position