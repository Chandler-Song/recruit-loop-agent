from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio
import uuid
from app.repositories.position import PositionRepository
from app.repositories.scheduler_job import SchedulerJobRepository
from app.models.scheduler_job import SchedulerJob
from app.services.runner import RunnerService


class SchedulerService:
    """
    Service for managing the scheduling of recruiting loops
    """
    
    def __init__(self, position_repo: PositionRepository, job_repo: SchedulerJobRepository, runner_service: RunnerService):
        self.position_repo = position_repo
        self.job_repo = job_repo
        self.runner_service = runner_service
        self.scheduler = AsyncIOScheduler()
        
    async def start(self):
        """
        Start the scheduler
        """
        if not self.scheduler.running:
            self.scheduler.start()
            
            # Schedule periodic check for active positions
            self.scheduler.add_job(
                self._check_and_schedule_positions,
                trigger=IntervalTrigger(seconds=60),  # Check every minute
                id='position_checker',
                name='Check positions for scheduling',
                replace_existing=True
            )
    
    async def stop(self):
        """
        Stop the scheduler
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
    
    async def schedule_position(self, position_id: uuid.UUID, interval_minutes: int = 60):
        """
        Schedule a position for recruiting loops
        """
        # Create or update scheduler job record
        job_data = {
            "position_id": position_id,
            "enabled": True,
            "interval_minutes": interval_minutes,
            "next_run": datetime.utcnow() + timedelta(minutes=interval_minutes),
            "status": "waiting"
        }
        
        # Check if job already exists
        existing_job = await self.job_repo.get_by_position_id(position_id)
        if existing_job:
            # Update existing job
            await self.job_repo.update(existing_job.id, job_data)
        else:
            # Create new job
            await self.job_repo.create(job_data)
        
        # Add job to scheduler
        self.scheduler.add_job(
            self._run_position_loop,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=f'position_{position_id}',
            name=f'Run recruiting loop for position {position_id}',
            args=[position_id],
            replace_existing=True
        )
    
    async def unschedule_position(self, position_id: uuid.UUID):
        """
        Remove a position from the scheduler
        """
        # Remove from scheduler
        job_id = f'position_{position_id}'
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Update job record
        existing_job = await self.job_repo.get_by_position_id(position_id)
        if existing_job:
            await self.job_repo.update_status(position_id, "paused")
    
    async def _run_position_loop(self, position_id: uuid.UUID):
        """
        Internal method to run the recruiting loop for a position
        """
        try:
            # Update job status to running
            await self.job_repo.update_status(position_id, "running")
            
            # Run the recruiting loop
            await self.runner_service.run_recruiting_loop(position_id)
            
            # Update job status to waiting
            await self.job_repo.update_status(position_id, "waiting")
            
            # Update last run time
            await self.job_repo.update_last_run(position_id, datetime.utcnow())
            
        except Exception as e:
            # Update job status to error
            await self.job_repo.update_status(position_id, "error")
            print(f"Error running recruiting loop for position {position_id}: {str(e)}")
    
    async def _check_and_schedule_positions(self):
        """
        Internal method to periodically check for active positions and schedule them
        """
        # Get all active positions
        positions = await self.position_repo.get_all(status="active")
        
        for position in positions:
            # Check if position should be scheduled
            if position.loop_enabled:
                # Get existing job
                existing_job = await self.job_repo.get_by_position_id(position.id)
                
                if not existing_job or existing_job.enabled:
                    # Schedule the position if not already scheduled
                    await self.schedule_position(position.id, position.loop_interval)
    
    async def get_job_status(self, position_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Get the status of a scheduled job
        """
        job = await self.job_repo.get_by_position_id(position_id)
        if not job:
            return None
        
        scheduler_job = self.scheduler.get_job(f'position_{position_id}')
        
        return {
            "position_id": job.position_id,
            "enabled": job.enabled,
            "interval_minutes": job.interval_minutes,
            "next_run": job.next_run,
            "last_run": job.last_run,
            "total_runs": job.total_runs,
            "status": job.status,
            "scheduler_active": scheduler_job is not None
        }
    
    async def pause_job(self, position_id: uuid.UUID):
        """
        Pause a scheduled job
        """
        await self.unschedule_position(position_id)
        await self.job_repo.update_status(position_id, "paused")
    
    async def resume_job(self, position_id: uuid.UUID):
        """
        Resume a scheduled job
        """
        position = await self.position_repo.get_by_id(position_id)
        if position:
            await self.schedule_position(position_id, position.loop_interval)
            await self.job_repo.update_status(position_id, "waiting")
    
    async def run_position_now(self, position_id: uuid.UUID):
        """
        Run a position's recruiting loop immediately
        """
        # Run the loop in the background
        asyncio.create_task(self._run_position_loop(position_id))