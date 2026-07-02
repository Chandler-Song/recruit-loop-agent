"""
Skills API tests
"""
import pytest


@pytest.mark.asyncio
async def test_get_skills(client):
    """Test getting skills"""
    response = await client.get("/api/v1/skills")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
