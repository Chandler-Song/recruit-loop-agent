from typing import List, Optional
from app.repositories.position import PositionRepository
from app.schemas.position import PositionCreate, PositionUpdate, Position
from app.core.exceptions import PositionNotFoundException
import uuid

class PositionService:
    def __init__(self, position_repo: PositionRepository):
        self.position_repo = position_repo

    async def create_position(self, position_data: PositionCreate) -> Position:
        return await self.position_repo.create(position_data)

    async def get_position_by_id(self, position_id: uuid.UUID) -> Position:
        position = await self.position_repo.get_by_id(position_id)
        if not position:
            raise PositionNotFoundException(f"Position with id {position_id} not found")
        return position

    async def get_all_positions(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Position]:
        return await self.position_repo.get_all(skip, limit, status)

    async def update_position(self, position_id: uuid.UUID, position_data: PositionUpdate) -> Optional[Position]:
        return await self.position_repo.update(position_id, position_data)

    async def delete_position(self, position_id: uuid.UUID) -> bool:
        return await self.position_repo.delete(position_id)

    async def pause_position(self, position_id: uuid.UUID) -> Optional[Position]:
        return await self.position_repo.update_status(position_id, "paused")

    async def resume_position(self, position_id: uuid.UUID) -> Optional[Position]:
        return await self.position_repo.update_status(position_id, "active")

    async def close_position(self, position_id: uuid.UUID) -> Optional[Position]:
        return await self.position_repo.update_status(position_id, "closed")