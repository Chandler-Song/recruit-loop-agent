"""
System API tests
"""
import pytest


@pytest.mark.asyncio
async def test_get_system_config(client):
    """Test getting system configuration"""
    response = await client.get("/api/v1/system/config")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Recruiting Loop Agent is running!"


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
