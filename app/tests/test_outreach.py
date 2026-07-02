"""
Outreach API tests
"""
import pytest


@pytest.mark.asyncio
async def test_get_outreach_logs(client):
    """Test getting outreach logs"""
    response = await client.get("/api/v1/outreach/logs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
