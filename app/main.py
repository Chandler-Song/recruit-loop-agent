from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
import uvicorn
from app.core.exception_handler import (
    recruiting_agent_exception_handler,
    position_not_found_exception_handler,
    candidate_not_found_exception_handler,
    pipeline_not_found_exception_handler,
    github_api_exception_handler,
    smtp_exception_handler,
    database_exception_handler,
    http_exception_handler
)
from app.core.exceptions import (
    RecruitingAgentException,
    PositionNotFoundException,
    CandidateNotFoundException,
    PipelineNotFoundException,
    GitHubAPIException,
    SMTPException,
    DatabaseException
)
from fastapi import HTTPException
from app.database.base import Base
from app.database.session import engine

app = FastAPI(
    title="Recruiting Loop Agent",
    description="An autonomous recruiting agent that continuously searches for candidates",
    version="3.0.0",
    redirect_slashes=False
)

# CORS middleware - allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RecruitingAgentException, recruiting_agent_exception_handler)
app.add_exception_handler(PositionNotFoundException, position_not_found_exception_handler)
app.add_exception_handler(CandidateNotFoundException, candidate_not_found_exception_handler)
app.add_exception_handler(PipelineNotFoundException, pipeline_not_found_exception_handler)
app.add_exception_handler(GitHubAPIException, github_api_exception_handler)
app.add_exception_handler(SMTPException, smtp_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Recruiting Loop Agent is running!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Create database tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)