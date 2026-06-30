class RecruitingAgentException(Exception):
    """Base exception for Recruiting Loop Agent"""
    pass


class PositionNotFoundException(RecruitingAgentException):
    """Raised when a position is not found"""
    pass


class CandidateNotFoundException(RecruitingAgentException):
    """Raised when a candidate is not found"""
    pass


class PipelineNotFoundException(RecruitingAgentException):
    """Raised when a pipeline is not found"""
    pass


class GitHubAPIException(RecruitingAgentException):
    """Raised when GitHub API returns an error"""
    pass


class SMTPException(RecruitingAgentException):
    """Raised when SMTP operations fail"""
    pass


class DatabaseException(RecruitingAgentException):
    """Raised when database operations fail"""
    pass