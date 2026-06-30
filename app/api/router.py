from fastapi import APIRouter
from app.api import dashboard, positions, candidates, pipelines, outreach, scheduler, skills, system

router = APIRouter()

# Include all API routers
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(positions.router, prefix="/positions", tags=["positions"])
router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
router.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])
router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
router.include_router(skills.router, prefix="/skills", tags=["skills"])
router.include_router(system.router, prefix="/system", tags=["system"])