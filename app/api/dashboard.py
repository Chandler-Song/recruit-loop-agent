from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary():
    return {"running_positions": 0, "today_loops": 0, "today_candidates": 0, "today_emails": 0, "today_replies": 0, "today_errors": 0}