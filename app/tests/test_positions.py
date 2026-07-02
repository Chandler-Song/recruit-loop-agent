"""
Positions API tests
"""
import pytest
import uuid


@pytest.mark.asyncio
async def test_create_position(client, sample_position_data):
    """Test creating a new position"""
    response = await client.post("/api/v1/positions", json=sample_position_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["title"] == sample_position_data["title"]
    assert data["company"] == sample_position_data["company"]
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_positions(client, sample_position_data):
    """Test getting all positions"""
    # Create a position first
    await client.post("/api/v1/positions", json=sample_position_data)
    
    response = await client.get("/api/v1/positions")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_positions_with_pagination(client, sample_position_data):
    """Test getting positions with pagination"""
    # Create multiple positions
    for i in range(3):
        data = sample_position_data.copy()
        data["title"] = f"Position {i}"
        await client.post("/api/v1/positions", json=data)
    
    response = await client.get("/api/v1/positions?skip=0&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_positions_with_status_filter(client, sample_position_data):
    """Test getting positions with status filter"""
    await client.post("/api/v1/positions", json=sample_position_data)
    
    response = await client.get("/api/v1/positions?status=active")
    
    assert response.status_code == 200
    data = response.json()
    assert all(pos["status"] == "active" for pos in data)


@pytest.mark.asyncio
async def test_get_position_by_id(client, sample_position_data):
    """Test getting a specific position by ID"""
    create_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = create_response.json()["id"]
    
    response = await client.get(f"/api/v1/positions/{position_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == position_id
    assert data["title"] == sample_position_data["title"]


@pytest.mark.asyncio
async def test_get_position_not_found(client):
    """Test getting a non-existent position"""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/positions/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_position(client, sample_position_data):
    """Test updating a position"""
    create_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = create_response.json()["id"]
    
    update_data = {"title": "Updated Title", "company": "Updated Company"}
    response = await client.put(f"/api/v1/positions/{position_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["company"] == "Updated Company"


@pytest.mark.asyncio
async def test_update_position_not_found(client):
    """Test updating a non-existent position"""
    fake_id = str(uuid.uuid4())
    update_data = {"title": "Updated Title"}
    response = await client.put(f"/api/v1/positions/{fake_id}", json=update_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_position(client, sample_position_data):
    """Test deleting a position"""
    create_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = create_response.json()["id"]
    
    response = await client.delete(f"/api/v1/positions/{position_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Position deleted successfully"
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/positions/{position_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_position_not_found(client):
    """Test deleting a non-existent position"""
    fake_id = str(uuid.uuid4())
    response = await client.delete(f"/api/v1/positions/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pause_position(client, sample_position_data):
    """Test pausing a position"""
    create_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = create_response.json()["id"]
    
    response = await client.post(f"/api/v1/positions/{position_id}/pause")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paused"
    assert data["loop_enabled"] == False


@pytest.mark.asyncio
async def test_resume_position(client, sample_position_data):
    """Test resuming a paused position"""
    create_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = create_response.json()["id"]
    
    # Pause first
    await client.post(f"/api/v1/positions/{position_id}/pause")
    
    # Then resume
    response = await client.post(f"/api/v1/positions/{position_id}/resume")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["loop_enabled"] == True


@pytest.mark.asyncio
async def test_close_position(client, sample_position_data):
    """Test closing a position"""
    create_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = create_response.json()["id"]
    
    response = await client.post(f"/api/v1/positions/{position_id}/close")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
