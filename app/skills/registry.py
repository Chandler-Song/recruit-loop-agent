from typing import Dict, Type, List
from app.skills.base import BaseSkill
from app.skills.github import GitHubSkill


class SkillRegistry:
    """
    Registry for all available skills in the Recruiting Loop Agent
    """
    
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._skill_classes: Dict[str, Type[BaseSkill]] = {
            "github_search": GitHubSkill
        }
        
    def register_skill(self, skill_name: str, skill_instance: BaseSkill):
        """
        Register a new skill instance
        """
        self._skills[skill_name] = skill_instance
        
    def get_skill(self, skill_name: str) -> BaseSkill:
        """
        Get a skill instance by name
        """
        if skill_name not in self._skills:
            if skill_name in self._skill_classes:
                # Create and register the skill if it's not already registered
                skill_instance = self._skill_classes[skill_name]()
                self.register_skill(skill_name, skill_instance)
            else:
                raise ValueError(f"Skill '{skill_name}' not found in registry")
                
        return self._skills[skill_name]
        
    def get_all_skills(self) -> List[BaseSkill]:
        """
        Get all available skills
        """
        return list(self._skills.values())
        
    def get_available_skill_names(self) -> List[str]:
        """
        Get names of all available skills
        """
        return list(self._skill_classes.keys())


# Global skill registry instance
skill_registry = SkillRegistry()