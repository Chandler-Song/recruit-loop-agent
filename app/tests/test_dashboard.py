"""
Dashboard API tests
"""
import pytest


@pytest.mark.asyncio
async def test_get_dashboard_summary(client):
    """Test getting dashboard summary"""
    response = await client.get("/api/v1/dashboard/summary")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "running_positions" in data
    assert "today_loops" in data
    assert "today_candidates" in data
    assert "today_emails" in data
    assert "today_replies" in data
    assert "today_errors" in data
    
    assert isinstance(data["running_positions"], int)
    assert isinstance(data["today_loops"], int)
    assert isinstance(data["today_candidates"], int)
    assert isinstance(data["today_emails"], int)
    assert isinstance(data["today_replies"], int)
    assert isinstance(data["today_errors"], int)
