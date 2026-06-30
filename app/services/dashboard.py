from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.repositories.position import PositionRepository
from app.repositories.agent_run import AgentRunRepository
from app.repositories.pipeline import PipelineRepository
from app.repositories.candidate import CandidateRepository
from app.repositories.node_log import NodeLogRepository
from app.models.position import Position
from app.models.agent_run import AgentRun
from app.models.pipeline import Pipeline
from app.models.candidate import Candidate
from app.models.node_log import NodeLog
import uuid


class DashboardService:
    """
    Service for retrieving dashboard metrics and statistics
    """
    
    def __init__(
        self,
        position_repo: PositionRepository,
        agent_run_repo: AgentRunRepository,
        pipeline_repo: PipelineRepository,
        candidate_repo: CandidateRepository,
        node_log_repo: NodeLogRepository
    ):
        self.position_repo = position_repo
        self.agent_run_repo = agent_run_repo
        self.pipeline_repo = pipeline_repo
        self.candidate_repo = candidate_repo
        self.node_log_repo = node_log_repo
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get the main dashboard summary metrics
        """
        # Get today's date for filtering
        today_start = datetime.combine(datetime.today().date(), datetime.min.time())
        
        # Count running positions
        active_positions = await self.position_repo.get_all(status="active")
        running_positions_count = len(active_positions)
        
        # Count today's agent runs
        all_runs = await self.agent_run_repo.get_all(skip=0, limit=1000)
        today_runs = [run for run in all_runs if run.started_at.date() == datetime.today().date()]
        today_loops = len(today_runs)
        
        # Count today's candidates
        all_candidates = await self.candidate_repo.get_all(skip=0, limit=1000)
        today_candidates = [cand for cand in all_candidates if cand.created_at.date() == datetime.today().date()]
        today_candidates_count = len(today_candidates)
        
        # Count today's emails sent (from agent runs)
        today_emails = sum(run.emails_sent for run in today_runs)
        
        # Count recent errors
        recent_errors = [run for run in all_runs if run.error and run.started_at.date() == datetime.today().date()]
        today_errors = len(recent_errors)
        
        # Count replies (candidates who have replied in pipeline)
        replied_candidates = await self.pipeline_repo.get_by_status(None, "replied")  # This would need to be filtered by date in practice
        
        return {
            "running_positions": running_positions_count,
            "today_loops": today_loops,
            "today_candidates": today_candidates_count,
            "today_emails": today_emails,
            "today_replies": len(replied_candidates),  # Placeholder
            "today_errors": today_errors
        }
    
    async def get_running_positions(self) -> List[Dict[str, Any]]:
        """
        Get information about currently running positions
        """
        active_positions = await self.position_repo.get_all(status="active")
        result = []
        
        for pos in active_positions:
            # Get recent pipeline stats for this position
            pipelines = await self.pipeline_repo.get_by_position(pos.id, skip=0, limit=100)
            
            # Calculate stats
            contacted_count = len([p for p in pipelines if p.status == "contacted"])
            
            result.append({
                "id": pos.id,
                "title": pos.title,
                "company": pos.company,
                "status": pos.status,
                "last_loop_at": pos.last_loop_at,
                "next_loop_at": pos.next_loop_at,
                "candidate_count": len(pipelines),
                "contacted_count": contacted_count
            })
        
        return result
    
    async def get_recent_activity(self) -> List[Dict[str, Any]]:
        """
        Get recent activity timeline
        """
        # Get recent agent runs and node logs
        recent_runs = await self.agent_run_repo.get_all(skip=0, limit=20)
        recent_logs = await self.node_log_repo.get_all(skip=0, limit=50)
        
        activities = []
        
        # Add agent runs to activities
        for run in recent_runs[-10:]:  # Last 10 runs
            activities.append({
                "time": run.started_at.strftime("%H:%M"),
                "type": "loop",
                "message": f"Loop completed for position {str(run.position_id)[:8]}",
                "details": {
                    "candidates_found": run.candidates_found,
                    "candidates_added": run.candidates_added,
                    "emails_sent": run.emails_sent
                }
            })
        
        # Add node logs to activities
        for log in recent_logs[-10:]:  # Last 10 logs
            activities.append({
                "time": log.started_at.strftime("%H:%M"),
                "type": log.node_name,
                "message": f"{log.node_name.capitalize()} node executed",
                "details": {
                    "status": log.status,
                    "duration_ms": log.duration_ms
                }
            })
        
        # Sort by time (most recent first)
        activities.sort(key=lambda x: x["time"], reverse=True)
        
        return activities[:20]  # Return top 20
    
    async def get_recent_errors(self) -> List[Dict[str, Any]]:
        """
        Get recent errors from agent runs and node logs
        """
        all_runs = await self.agent_run_repo.get_all(skip=0, limit=100)
        all_logs = await self.node_log_repo.get_all(skip=0, limit=100)
        
        errors = []
        
        # Get errors from agent runs
        for run in all_runs:
            if run.error:
                errors.append({
                    "time": run.started_at.strftime("%H:%M"),
                    "source": "agent_run",
                    "message": run.error,
                    "position_id": str(run.position_id)
                })
        
        # Get errors from node logs
        for log in all_logs:
            if log.error:
                errors.append({
                    "time": log.started_at.strftime("%H:%M"),
                    "source": log.node_name,
                    "message": log.error,
                    "position_id": "unknown"  # Would need to trace back to position
                })
        
        # Sort by time (most recent first)
        errors.sort(key=lambda x: x["time"], reverse=True)
        
        return errors[:10]  # Return top 10
    
    async def get_position_stats(self, position_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific position
        """
        position = await self.position_repo.get_by_id(position_id)
        if not position:
            return {}
        
        # Get pipelines for this position
        pipelines = await self.pipeline_repo.get_by_position(position_id, skip=0, limit=1000)
        
        # Count by status
        status_counts = {}
        for pipeline in pipelines:
            status = pipeline.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get related agent runs
        runs = await self.agent_run_repo.get_by_position(position_id, skip=0, limit=100)
        
        # Calculate metrics
        total_candidates = len(pipelines)
        contacted_count = status_counts.get("contacted", 0)
        replied_count = status_counts.get("replied", 0)
        total_emails_sent = sum(run.emails_sent for run in runs)
        
        return {
            "position": {
                "id": position.id,
                "title": position.title,
                "company": position.company,
                "status": position.status,
                "created_at": position.created_at
            },
            "pipeline_stats": status_counts,
            "metrics": {
                "total_candidates": total_candidates,
                "contacted": contacted_count,
                "replied": replied_count,
                "total_emails_sent": total_emails_sent,
                "total_runs": len(runs)
            },
            "recent_runs": [
                {
                    "id": run.id,
                    "started_at": run.started_at,
                    "finished_at": run.finished_at,
                    "duration_ms": run.duration_ms,
                    "candidates_found": run.candidates_found,
                    "candidates_added": run.candidates_added,
                    "emails_sent": run.emails_sent,
                    "status": run.status
                } for run in runs[-5:]  # Last 5 runs
            ]
        }