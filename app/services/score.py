from typing import List, Dict, Any
from app.models.candidate import Candidate
from app.models.pipeline import Pipeline
from app.schemas.pipeline import PipelineUpdate
import json

class ScoreService:
    """
    Service for calculating scores for candidates based on various factors
    """
    
    def __init__(self):
        # Weights for different scoring criteria
        self.skill_weight = 0.5  # 50% of total score
        self.activity_weight = 0.3  # 30% of total score
        self.profile_weight = 0.2  # 20% of total score
    
    async def calculate_score(self, candidate: Candidate, required_skills: List[str]) -> Dict[str, Any]:
        """
        Calculate a score for a candidate based on required skills, activity, and profile completeness
        """
        # Calculate skill score (0-100)
        skill_score = self._calculate_skill_score(candidate, required_skills)
        
        # Calculate activity score (0-100)
        activity_score = self._calculate_activity_score(candidate)
        
        # Calculate profile score (0-100)
        profile_score = self._calculate_profile_score(candidate)
        
        # Calculate weighted total score
        total_score = (
            skill_score * self.skill_weight +
            activity_score * self.activity_weight +
            profile_score * self.profile_weight
        )
        
        score_detail = {
            "skill_score": skill_score,
            "activity_score": activity_score,
            "profile_score": profile_score,
            "weights": {
                "skill": self.skill_weight,
                "activity": self.activity_weight,
                "profile": self.profile_weight
            },
            "breakdown": {
                "skills_match": self._get_skills_match(candidate, required_skills)
            }
        }
        
        return {
            "total_score": round(total_score, 2),
            "detail": score_detail
        }
    
    def _calculate_skill_score(self, candidate: Candidate, required_skills: List[str]) -> float:
        """
        Calculate skill-based score
        """
        if not required_skills or not candidate.skills:
            return 0.0
            
        # Parse skills from JSON string if needed
        candidate_skills_list = candidate.skills if isinstance(candidate.skills, list) else []
        if isinstance(candidate.skills, str):
            try:
                candidate_skills_list = json.loads(candidate.skills)
            except:
                candidate_skills_list = []
        
        matched_skills = [skill for skill in required_skills if skill.lower() in [s.lower() for s in candidate_skills_list]]
        score = (len(matched_skills) / len(required_skills)) * 100
        
        return min(score, 100.0)  # Cap at 100
    
    def _calculate_activity_score(self, candidate: Candidate) -> float:
        """
        Calculate activity-based score based on GitHub metrics
        """
        # Followers contribute up to 40 points
        followers_score = min((candidate.followers / 100) * 40, 40)
        
        # Public repos contribute up to 30 points
        repos_score = min((candidate.public_repos / 20) * 30, 30)
        
        # Combined activity score (max 70)
        activity_score = followers_score + repos_score
        
        # Normalize to 0-100 scale
        normalized_score = (activity_score / 70) * 100 if activity_score > 0 else 0
        
        return min(normalized_score, 100.0)
    
    def _calculate_profile_score(self, candidate: Candidate) -> float:
        """
        Calculate profile completeness score
        """
        score = 0
        
        # Name present
        if candidate.name:
            score += 15
        
        # Location present
        if candidate.location:
            score += 10
            
        # Company present
        if candidate.company:
            score += 10
            
        # Bio present
        if candidate.bio:
            score += 20
            
        # Profile URL present
        if candidate.profile_url:
            score += 15
            
        # Avatar URL present
        if candidate.avatar_url:
            score += 10
            
        # Email present
        if candidate.email:
            score += 20
            
        return min(score, 100.0)
    
    def _get_skills_match(self, candidate: Candidate, required_skills: List[str]) -> Dict[str, Any]:
        """
        Get details about skills match for reporting
        """
        candidate_skills_list = candidate.skills if isinstance(candidate.skills, list) else []
        if isinstance(candidate.skills, str):
            try:
                candidate_skills_list = json.loads(candidate.skills)
            except:
                candidate_skills_list = []
        
        matched_skills = [skill for skill in required_skills if skill.lower() in [s.lower() for s in candidate_skills_list]]
        unmatched_skills = [skill for skill in required_skills if skill.lower() not in [s.lower() for s in candidate_skills_list]]
        
        return {
            "matched": matched_skills,
            "unmatched": unmatched_skills,
            "match_percentage": len(matched_skills) / len(required_skills) * 100 if required_skills else 0
        }
    
    async def should_add_to_pipeline(self, score: float, threshold: float = 60.0) -> bool:
        """
        Determine if a candidate should be added to the pipeline based on score
        """
        return score >= threshold