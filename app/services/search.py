from typing import List, Dict, Any
from app.skills.registry import skill_registry
from app.services.candidate import CandidateService
from app.repositories.candidate import CandidateRepository
from app.models.candidate import Candidate
from app.core.exceptions import GitHubAPIException
import asyncio


class SearchService:
    """
    Service for handling candidate searches across different platforms
    """
    
    def __init__(self, candidate_service: CandidateService):
        self.candidate_service = candidate_service
        self.skill_registry = skill_registry
    
    async def search_candidates(self, position_id: str, keywords: List[str], max_results: int = 100) -> List[Candidate]:
        """
        Search for candidates using various skills
        """
        all_candidates = []
        
        # Use GitHub skill to search for candidates
        try:
            github_skill = self.skill_registry.get_skill("github_search")
            github_results = await github_skill.execute(keywords, max_results)
            
            # Convert results to candidate objects
            for candidate_data in github_results:
                # Create or update candidate in the database
                candidate_create_data = {
                    "source": candidate_data["source"],
                    "source_id": candidate_data["source_id"],
                    "github_login": candidate_data["github_login"],
                    "name": candidate_data["name"],
                    "email": candidate_data["email"],
                    "location": candidate_data["location"],
                    "company": candidate_data["company"],
                    "title": candidate_data["title"],
                    "bio": candidate_data["bio"],
                    "followers": candidate_data["followers"],
                    "public_repos": candidate_data["public_repos"],
                    "profile_url": candidate_data["profile_url"],
                    "avatar_url": candidate_data["avatar_url"],
                    "skills": candidate_data["skills"],
                    "search_keywords": candidate_data["search_keywords"]
                }
                
                # Create candidate (this will handle deduplication)
                candidate = await self.candidate_service.create_candidate(candidate_create_data)
                all_candidates.append(candidate)
                
        except GitHubAPIException as e:
            # Log the error but continue with other skills if available
            print(f"GitHub search failed: {str(e)}")
        except Exception as e:
            print(f"Unexpected error during search: {str(e)}")
        
        return all_candidates
    
    async def generate_search_keywords(self, position_title: str, required_skills: List[str], search_keywords: List[str]) -> List[str]:
        """
        Generate comprehensive search keywords based on position requirements
        """
        keywords = []
        
        # Add position title keywords
        if position_title:
            keywords.extend([position_title.lower(), position_title.replace(" ", "+")])
        
        # Add required skills
        if required_skills:
            keywords.extend(required_skills)
            # Combine skills for more specific searches
            for i in range(len(required_skills)):
                for j in range(i+1, len(required_skills)):
                    combined = f"{required_skills[i]}+{required_skills[j]}"
                    keywords.append(combined)
        
        # Add custom search keywords
        if search_keywords:
            keywords.extend(search_keywords)
        
        # Remove duplicates while preserving order
        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)
        
        return unique_keywords