from typing import List, Optional
from app.repositories.pipeline import PipelineRepository
from app.schemas.pipeline import PipelineCreate, PipelineUpdate, Pipeline
from app.core.exceptions import PipelineNotFoundException
import uuid

class PipelineService:
    def __init__(self, pipeline_repo: PipelineRepository):
        self.pipeline_repo = pipeline_repo

    async def create_pipeline(self, pipeline_data: PipelineCreate) -> Pipeline:
        # Check if pipeline already exists for this position and candidate
        existing_pipeline = await self.pipeline_repo.get_by_position_and_candidate(
            pipeline_data.position_id,
            pipeline_data.candidate_id
        )
        
        if existing_pipeline:
            # Return existing pipeline instead of creating duplicate
            return existing_pipeline
        
        return await self.pipeline_repo.create(pipeline_data)

    async def get_pipeline_by_id(self, pipeline_id: uuid.UUID) -> Pipeline:
        pipeline = await self.pipeline_repo.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with id {pipeline_id} not found")
        return pipeline

    async def get_pipeline_by_position_and_candidate(self, position_id: uuid.UUID, candidate_id: uuid.UUID) -> Optional[Pipeline]:
        return await self.pipeline_repo.get_by_position_and_candidate(position_id, candidate_id)

    async def get_pipelines_by_position(self, position_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Pipeline]:
        return await self.pipeline_repo.get_by_position(position_id, skip, limit)

    async def get_pipelines_by_status(self, position_id: uuid.UUID, status: str) -> List[Pipeline]:
        return await self.pipeline_repo.get_by_status(position_id, status)

    async def get_all_pipelines(self, skip: int = 0, limit: int = 100) -> List[Pipeline]:
        return await self.pipeline_repo.get_all(skip, limit)

    async def update_pipeline(self, pipeline_id: uuid.UUID, pipeline_data: PipelineUpdate) -> Optional[Pipeline]:
        return await self.pipeline_repo.update(pipeline_id, pipeline_data)

    async def update_pipeline_status(self, pipeline_id: uuid.UUID, status: str) -> Optional[Pipeline]:
        return await self.pipeline_repo.update_status(pipeline_id, status)

    async def delete_pipeline(self, pipeline_id: uuid.UUID) -> bool:
        return await self.pipeline_repo.delete(pipeline_id)

    async def move_to_next_stage(self, pipeline_id: uuid.UUID) -> Optional[Pipeline]:
        """
        Move pipeline to the next stage in the recruitment process
        discovered -> contacted -> replied -> interview -> offer -> rejected
        """
        pipeline = await self.get_pipeline_by_id(pipeline_id)
        if pipeline:
            current_status = pipeline.status
            if current_status == "discovered":
                next_status = "contacted"
            elif current_status == "contacted":
                next_status = "replied"
            elif current_status == "replied":
                next_status = "interview"
            elif current_status == "interview":
                next_status = "offer"
            elif current_status == "offer":
                next_status = "rejected"
            else:
                next_status = current_status
            
            if current_status != next_status:
                return await self.update_pipeline_status(pipeline_id, next_status)
        
        return pipeline