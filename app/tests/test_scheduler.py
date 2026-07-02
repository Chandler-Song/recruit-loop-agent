"""
Scheduler API tests
"""
import pytest


@pytest.mark.asyncio
async def test_get_scheduler_jobs(client):
    """Test getting scheduler jobs"""
    response = await client.get("/api/v1/scheduler/jobs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
