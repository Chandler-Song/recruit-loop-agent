from typing import Dict, Any, List
from app.services.search import SearchService
from app.services.score import ScoreService
from app.services.pipeline import PipelineService
from app.services.email import EmailService
from app.repositories.candidate import CandidateRepository
from app.repositories.position import PositionRepository
from app.repositories.pipeline import PipelineRepository
from app.repositories.outreach_log import OutreachLogRepository
from app.repositories.agent_run import AgentRunRepository
from app.repositories.node_log import NodeLogRepository
from app.models.candidate import Candidate
from app.models.position import Position
from app.models.pipeline import Pipeline
from app.models.agent_run import AgentRun
from app.models.node_log import NodeLog
from app.schemas.agent_run import AgentRunCreate
from app.schemas.node_log import NodeLogCreate
from app.core.exceptions import DatabaseException
from datetime import datetime
import uuid
import asyncio
import time


class RunnerService:
    """
    Service to coordinate the entire recruiting loop: Search -> Dedup -> Score -> Pipeline -> Outreach -> Evaluate
    """
    
    def __init__(
        self,
        search_service: SearchService,
        score_service: ScoreService,
        pipeline_service: PipelineService,
        email_service: EmailService,
        candidate_repo: CandidateRepository,
        position_repo: PositionRepository,
        pipeline_repo: PipelineRepository,
        outreach_log_repo: OutreachLogRepository,
        agent_run_repo: AgentRunRepository,
        node_log_repo: NodeLogRepository
    ):
        self.search_service = search_service
        self.score_service = score_service
        self.pipeline_service = pipeline_service
        self.email_service = email_service
        self.candidate_repo = candidate_repo
        self.position_repo = position_repo
        self.pipeline_repo = pipeline_repo
        self.outreach_log_repo = outreach_log_repo
        self.agent_run_repo = agent_run_repo
        self.node_log_repo = node_log_repo
    
    async def run_recruiting_loop(self, position_id: uuid.UUID) -> Dict[str, Any]:
        """
        Execute the full recruiting loop for a position
        """
        start_time = time.time()
        
        # Create an agent run record
        agent_run_data = AgentRunCreate(
            position_id=position_id,
            started_at=datetime.utcnow(),
            status="running"
        )
        agent_run = await self.agent_run_repo.create(agent_run_data)
        
        try:
            # Get position details
            position = await self.position_repo.get_by_id(position_id)
            if not position:
                raise ValueError(f"Position {position_id} not found")
            
            # Prepare results tracking
            results = {
                "candidates_found": 0,
                "candidates_added": 0,
                "emails_sent": 0,
                "errors": []
            }
            
            # Node 1: Search
            search_start = time.time()
            try:
                # Generate search keywords based on position requirements
                keywords = await self.search_service.generate_search_keywords(
                    position.title,
                    position.required_skills or [],
                    position.search_keywords or []
                )
                
                # Search for candidates
                candidates = await self.search_service.search_candidates(
                    str(position_id),
                    keywords,
                    max_results=100
                )
                
                results["candidates_found"] = len(candidates)
                results["candidates"] = candidates
                
                # Log successful search
                search_duration = time.time() - search_start
                await self._log_node_result(agent_run.id, "search", "success", search_duration, {
                    "keywords_used": keywords,
                    "candidates_found": len(candidates)
                })
                
            except Exception as e:
                error_msg = f"Search failed: {str(e)}"
                results["errors"].append(error_msg)
                search_duration = time.time() - search_start
                await self._log_node_result(agent_run.id, "search", "failed", search_duration, {
                    "error": error_msg
                })
                # Continue with the rest of the loop despite search error
            
            # Node 2: Score (if candidates were found)
            score_start = time.time()
            try:
                scored_candidates = []
                if "candidates" in results:
                    for candidate in results["candidates"]:
                        # Calculate score for candidate
                        score_result = await self.score_service.calculate_score(
                            candidate,
                            position.required_skills or []
                        )
                        
                        # Check if candidate should be added to pipeline
                        should_add = await self.score_service.should_add_to_pipeline(
                            score_result["total_score"]
                        )
                        
                        if should_add:
                            # Create pipeline entry for candidate
                            pipeline_data = {
                                "position_id": position_id,
                                "candidate_id": candidate.id,
                                "score": score_result["total_score"],
                                "score_detail": str(score_result["detail"]),
                                "status": "discovered"
                            }
                            
                            pipeline = await self.pipeline_service.create_pipeline(pipeline_data)
                            scored_candidates.append({
                                "candidate": candidate,
                                "pipeline": pipeline,
                                "score": score_result["total_score"]
                            })
                
                results["scored_candidates"] = scored_candidates
                
                # Log successful scoring
                score_duration = time.time() - score_start
                await self._log_node_result(agent_run.id, "score", "success", score_duration, {
                    "candidates_scored": len(results["scored_candidates"])
                })
                
            except Exception as e:
                error_msg = f"Scoring failed: {str(e)}"
                results["errors"].append(error_msg)
                score_duration = time.time() - score_start
                await self._log_node_result(agent_run.id, "score", "failed", score_duration, {
                    "error": error_msg
                })
            
            # Node 3: Outreach (send emails to top candidates)
            outreach_start = time.time()
            try:
                emails_sent = 0
                if "scored_candidates" in results:
                    # Sort candidates by score and send emails to top ones
                    sorted_candidates = sorted(
                        results["scored_candidates"],
                        key=lambda x: x["score"],
                        reverse=True
                    )[:10]  # Top 10 candidates
                    
                    for item in sorted_candidates:
                        candidate = item["candidate"]
                        pipeline = item["pipeline"]
                        
                        # Generate and send email
                        email_body = self.email_service.generate_email_template(
                            candidate.name or candidate.github_login or "Candidate",
                            position.title,
                            position.company
                        )
                        
                        if candidate.email:  # Only send if we have an email
                            try:
                                success = await self.email_service.send_email(
                                    candidate.email,
                                    f"Opportunity at {position.company}: {position.title}",
                                    email_body,
                                    pipeline.id
                                )
                                
                                if success:
                                    emails_sent += 1
                                    
                                    # Update pipeline status to contacted
                                    await self.pipeline_service.update_pipeline_status(
                                        pipeline.id,
                                        "contacted"
                                    )
                            except Exception as email_error:
                                error_msg = f"Email failed for candidate {candidate.id}: {str(email_error)}"
                                results["errors"].append(error_msg)
                
                results["emails_sent"] = emails_sent
                
                # Log successful outreach
                outreach_duration = time.time() - outreach_start
                await self._log_node_result(agent_run.id, "outreach", "success", outreach_duration, {
                    "emails_sent": emails_sent
                })
                
            except Exception as e:
                error_msg = f"Outreach failed: {str(e)}"
                results["errors"].append(error_msg)
                outreach_duration = time.time() - outreach_start
                await self._log_node_result(agent_run.id, "outreach", "failed", outreach_duration, {
                    "error": error_msg
                })
            
            # Update results
            results["candidates_added"] = len(results.get("scored_candidates", []))
            results["emails_sent"] = results.get("emails_sent", 0)
            
            # Update agent run with final results
            duration_ms = int((time.time() - start_time) * 1000)
            await self.agent_run_repo.update_completion(
                agent_run.id,
                "success",
                duration_ms,
                results["candidates_found"],
                results["candidates_added"],
                results["emails_sent"]
            )
            
            return {
                "status": "completed",
                "results": results,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            # Handle critical error in the loop
            duration_ms = int((time.time() - start_time) * 1000)
            await self.agent_run_repo.update_completion(
                agent_run.id,
                "failed",
                duration_ms,
                0,
                0,
                0,
                str(e)
            )
            
            return {
                "status": "failed",
                "error": str(e),
                "duration_ms": duration_ms
            }
    
    async def _log_node_result(
        self,
        run_id: uuid.UUID,
        node_name: str,
        status: str,
        duration: float,
        data: Dict[str, Any]
    ):
        """
        Log the result of a specific node in the recruiting loop
        """
        node_log_data = NodeLogCreate(
            run_id=run_id,
            node_name=node_name,
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            duration_ms=int(duration * 1000),  # Convert to milliseconds
            status=status,
            input=str(data.get("input", {})),
            output=str(data.get("output", {})),
            error=data.get("error", "")
        )
        
        await self.node_log_repo.create(node_log_data)