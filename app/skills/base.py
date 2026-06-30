from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models.candidate import Candidate


class BaseSkill(ABC):
    """
    Base class for all skills in the Recruiting Loop Agent
    """

    @abstractmethod
    async def execute(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute the skill and return a list of candidate data
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the skill
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Return the description of the skill
        """
        pass