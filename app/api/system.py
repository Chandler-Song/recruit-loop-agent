from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
async def get_system_config():
    return {}