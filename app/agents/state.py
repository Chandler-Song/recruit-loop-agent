from typing import TypedDict, List, Dict, Any, Optional
from app.models.candidate import Candidate
from app.models.position import Position
import uuid


class RecruitingState(TypedDict):
    """
    State for the recruiting loop agent
    """
    position: Position
    keywords: List[str]
    candidates: List[Dict[str, Any]]
    dedup_result: List[Dict[str, Any]]
    pipeline_updates: List[Dict[str, Any]]
    metrics: Dict[str, int]
    errors: List[str]
    continue_loop: bool
    run_id: Optional[uuid.UUID]