from typing import Dict, Any, List
from app.agents.state import RecruitingState
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
import asyncio


async def search_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Search node: Perform candidate search based on position requirements
    """
    try:
        # This would integrate with the SearchService
        position = state["position"]
        
        # Generate search keywords based on position requirements
        keywords = [position.title] + (position.required_skills or []) + (position.search_keywords or [])
        
        # Simulate search (in real implementation, this would call SearchService)
        # For now, return empty results as the actual search happens in RunnerService
        search_results = {
            "keywords": keywords,
            "candidates": state.get("candidates", []),
            "found_count": len(state.get("candidates", []))
        }
        
        # Update metrics
        metrics = state.get("metrics", {})
        metrics["search_count"] = metrics.get("search_count", 0) + 1
        
        return {
            **state,
            "keywords": keywords,
            "candidates": state.get("candidates", []),
            "metrics": metrics
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Search node error: {str(e)}")
        
        return {
            **state,
            "errors": errors
        }


async def dedup_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Deduplication node: Remove duplicate candidates
    """
    try:
        candidates = state.get("candidates", [])
        
        # In a real implementation, this would use CandidateService's deduplication methods
        # For now, simulate deduplication by keeping unique candidates based on source_id
        seen_ids = set()
        unique_candidates = []
        
        for candidate in candidates:
            # Extract source and source_id from candidate data
            source_id = candidate.get("source_id") or (candidate.get("id") if hasattr(candidate, "id") else None)
            if source_id not in seen_ids:
                seen_ids.add(source_id)
                unique_candidates.append(candidate)
        
        dedup_result = {
            "original_count": len(candidates),
            "unique_count": len(unique_candidates),
            "duplicates_removed": len(candidates) - len(unique_candidates)
        }
        
        # Update metrics
        metrics = state.get("metrics", {})
        metrics["candidates_deduped"] = len(unique_candidates)
        
        return {
            **state,
            "dedup_result": [unique_candidates],
            "candidates": unique_candidates,
            "metrics": metrics
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Dedup node error: {str(e)}")
        
        return {
            **state,
            "errors": errors
        }


async def score_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Scoring node: Score candidates based on position requirements
    """
    try:
        candidates = state.get("candidates", [])
        position = state["position"]
        
        # In a real implementation, this would use ScoreService
        # For now, simulate scoring
        scored_candidates = []
        for candidate in candidates:
            # Just add a dummy score for now - in real implementation, use ScoreService
            candidate_with_score = {**candidate, "score": 75.0}  # Default score
            scored_candidates.append(candidate_with_score)
        
        # Update metrics
        metrics = state.get("metrics", {})
        metrics["candidates_scored"] = len(scored_candidates)
        
        return {
            **state,
            "candidates": scored_candidates,
            "metrics": metrics
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Score node error: {str(e)}")
        
        return {
            **state,
            "errors": errors
        }


async def pipeline_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Pipeline node: Update pipeline with scored candidates
    """
    try:
        candidates = state.get("candidates", [])
        position = state["position"]
        
        # In a real implementation, this would use PipelineService
        # For now, simulate pipeline updates
        pipeline_updates = []
        for candidate in candidates:
            # Create a simulated pipeline update
            pipeline_update = {
                "candidate_id": candidate.get("id", "unknown"),
                "position_id": position.id,
                "status": "discovered",
                "score": candidate.get("score", 0)
            }
            pipeline_updates.append(pipeline_update)
        
        # Update metrics
        metrics = state.get("metrics", {})
        metrics["pipeline_updates"] = len(pipeline_updates)
        
        return {
            **state,
            "pipeline_updates": pipeline_updates,
            "metrics": metrics
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Pipeline node error: {str(e)}")
        
        return {
            **state,
            "errors": errors
        }


async def outreach_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Outreach node: Send communications to candidates
    """
    try:
        candidates = state.get("candidates", [])
        position = state["position"]
        
        # In a real implementation, this would use EmailService
        # For now, simulate outreach
        outreach_results = []
        for candidate in candidates[:5]:  # Only outreach to first 5 candidates
            # Simulate email sending
            outreach_result = {
                "candidate_id": candidate.get("id", "unknown"),
                "status": "sent",  # or "failed"
                "type": "email"
            }
            outreach_results.append(outreach_result)
        
        # Update metrics
        metrics = state.get("metrics", {})
        metrics["outreach_attempts"] = len(outreach_results)
        metrics["emails_sent"] = len(outreach_results)  # Assuming all attempts were successful
        
        return {
            **state,
            "metrics": metrics
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Outreach node error: {str(e)}")
        
        return {
            **state,
            "errors": errors
        }


async def evaluate_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Evaluation node: Decide whether to continue the loop
    """
    try:
        position = state["position"]
        
        # Determine if the position is still open
        # In a real implementation, this would check the position status
        continue_loop = position.status == "active"
        
        # Update metrics
        metrics = state.get("metrics", {})
        metrics["evaluation_completed"] = True
        
        return {
            **state,
            "continue_loop": continue_loop,
            "metrics": metrics
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Evaluate node error: {str(e)}")
        
        return {
            **state,
            "errors": errors,
            "continue_loop": False  # On error, stop the loop
        }