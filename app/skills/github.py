import httpx
from typing import List, Dict, Any
from app.skills.base import BaseSkill
from app.core.config import settings
from app.core.exceptions import GitHubAPIException
import asyncio

class GitHubSkill(BaseSkill):
    """
    GitHub search skill for the Recruiting Loop Agent
    """
    
    def __init__(self):
        self.github_token = settings.github_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Recruiting-Loop-Agent"
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
    
    async def execute(self, keywords: List[str], max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Execute GitHub search and return a list of candidate data
        """
        all_candidates = []
        
        for keyword in keywords:
            try:
                # Search users based on keyword
                search_url = f"https://api.github.com/search/users?q={keyword}&per_page=30"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(search_url, headers=self.headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        users = data.get("items", [])
                        
                        # Get detailed user information for each user
                        for user in users[:min(len(users), max_results//len(keywords))]:
                            user_details = await self._get_user_details(user["login"])
                            if user_details:
                                all_candidates.append(user_details)
                                
                        # Respect rate limits
                        await asyncio.sleep(1)
                    elif response.status_code == 403:
                        # Handle rate limiting
                        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                        current_time = int(asyncio.get_event_loop().time())
                        sleep_time = max(reset_time - current_time, 60)
                        await asyncio.sleep(sleep_time)
                        continue
                    else:
                        raise GitHubAPIException(f"GitHub API returned status code {response.status_code}")
                        
            except Exception as e:
                raise GitHubAPIException(f"Error searching GitHub for keyword '{keyword}': {str(e)}")
        
        return all_candidates
    
    async def _get_user_details(self, username: str) -> Dict[str, Any]:
        """
        Get detailed information about a GitHub user
        """
        try:
            user_url = f"https://api.github.com/users/{username}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(user_url, headers=self.headers)
                
                if response.status_code == 200:
                    user_data = response.json()
                    
                    # Format the user data to match our candidate model
                    candidate_data = {
                        "source": "github",
                        "source_id": str(user_data.get("id", "")),
                        "github_login": user_data.get("login", ""),
                        "name": user_data.get("name", ""),
                        "email": user_data.get("email", ""),
                        "location": user_data.get("location", ""),
                        "company": user_data.get("company", ""),
                        "bio": user_data.get("bio", ""),
                        "followers": user_data.get("followers", 0),
                        "public_repos": user_data.get("public_repos", 0),
                        "profile_url": user_data.get("html_url", ""),
                        "avatar_url": user_data.get("avatar_url", ""),
                        "title": "",  # GitHub doesn't have a direct title field
                        "skills": [],  # Skills would need to be inferred from repos
                        "search_keywords": []  # Will be populated later
                    }
                    
                    return candidate_data
                else:
                    return None
                    
        except Exception as e:
            raise GitHubAPIException(f"Error fetching details for user '{username}': {str(e)}")
    
    def name(self) -> str:
        return "github_search"
    
    def description(self) -> str:
        return "Searches GitHub for potential candidates based on keywords"