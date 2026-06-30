from fastapi import APIRouter

router = APIRouter()

@router.get("/jobs")
async def get_scheduler_jobs():
    return []