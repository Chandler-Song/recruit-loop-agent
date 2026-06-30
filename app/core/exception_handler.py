from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    RecruitingAgentException,
    PositionNotFoundException,
    CandidateNotFoundException,
    PipelineNotFoundException,
    GitHubAPIException,
    SMTPException,
    DatabaseException
)

async def recruiting_agent_exception_handler(request: Request, exc: RecruitingAgentException):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(exc),
            "error_code": "INTERNAL_ERROR"
        }
    )

async def position_not_found_exception_handler(request: Request, exc: PositionNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Position not found",
            "error_code": "POSITION_NOT_FOUND"
        }
    )

async def candidate_not_found_exception_handler(request: Request, exc: CandidateNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Candidate not found",
            "error_code": "CANDIDATE_NOT_FOUND"
        }
    )

async def pipeline_not_found_exception_handler(request: Request, exc: PipelineNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Pipeline not found",
            "error_code": "PIPELINE_NOT_FOUND"
        }
    )

async def github_api_exception_handler(request: Request, exc: GitHubAPIException):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"GitHub API Error: {str(exc)}",
            "error_code": "GITHUB_API_ERROR"
        }
    )

async def smtp_exception_handler(request: Request, exc: SMTPException):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"SMTP Error: {str(exc)}",
            "error_code": "SMTP_ERROR"
        }
    )

async def database_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"Database Error: {str(exc)}",
            "error_code": "DATABASE_ERROR"
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": "HTTP_ERROR"
        }
    )