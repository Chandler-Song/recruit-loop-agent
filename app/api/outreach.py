from fastapi import APIRouter

router = APIRouter()

@router.get("/logs")
async def get_outreach_logs():
    return []