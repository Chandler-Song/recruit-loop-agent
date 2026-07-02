"""
Candidates API tests
"""
import pytest
import uuid


@pytest.mark.asyncio
async def test_create_candidate(client, sample_candidate_data):
    """Test creating a new candidate"""
    response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["source"] == sample_candidate_data["source"]
    assert data["source_id"] == sample_candidate_data["source_id"]
    assert data["github_login"] == sample_candidate_data["github_login"]
    assert data["name"] == sample_candidate_data["name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["appearance_count"] == 1
    assert data["source_weight"] == 1.0


@pytest.mark.asyncio
async def test_create_duplicate_candidate(client, sample_candidate_data):
    """Test creating a duplicate candidate increments appearance count"""
    # Create first time
    response1 = await client.post("/api/v1/candidates", json=sample_candidate_data)
    assert response1.status_code == 200
    
    # Create duplicate
    response2 = await client.post("/api/v1/candidates", json=sample_candidate_data)
    assert response2.status_code == 200
    
    data = response2.json()
    assert data["appearance_count"] == 2
    assert data["source_weight"] == 2.0


@pytest.mark.asyncio
async def test_get_candidates(client, sample_candidate_data):
    """Test getting all candidates"""
    await client.post("/api/v1/candidates", json=sample_candidate_data)
    
    response = await client.get("/api/v1/candidates")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_candidates_with_pagination(client, sample_candidate_data):
    """Test getting candidates with pagination"""
    # Create multiple candidates
    for i in range(3):
        data = sample_candidate_data.copy()
        data["source_id"] = str(10000 + i)
        data["github_login"] = f"user{i}"
        await client.post("/api/v1/candidates", json=data)
    
    response = await client.get("/api/v1/candidates?skip=0&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_candidates_with_keyword_filter(client, sample_candidate_data):
    """Test getting candidates with keyword filter"""
    await client.post("/api/v1/candidates", json=sample_candidate_data)
    
    response = await client.get("/api/v1/candidates?keyword=John")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("John" in c.get("name", "") for c in data)


@pytest.mark.asyncio
async def test_get_candidate_by_id(client, sample_candidate_data):
    """Test getting a specific candidate by ID"""
    create_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = create_response.json()["id"]
    
    response = await client.get(f"/api/v1/candidates/{candidate_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == candidate_id
    assert data["name"] == sample_candidate_data["name"]


@pytest.mark.asyncio
async def test_get_candidate_not_found(client):
    """Test getting a non-existent candidate"""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/candidates/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_candidate(client, sample_candidate_data):
    """Test updating a candidate"""
    create_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = create_response.json()["id"]
    
    update_data = {"name": "Jane Doe", "title": "Senior Developer"}
    response = await client.put(f"/api/v1/candidates/{candidate_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["title"] == "Senior Developer"


@pytest.mark.asyncio
async def test_update_candidate_not_found(client):
    """Test updating a non-existent candidate"""
    fake_id = str(uuid.uuid4())
    update_data = {"name": "Updated Name"}
    response = await client.put(f"/api/v1/candidates/{fake_id}", json=update_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_candidate(client, sample_candidate_data):
    """Test deleting a candidate"""
    create_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = create_response.json()["id"]
    
    response = await client.delete(f"/api/v1/candidates/{candidate_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Candidate deleted successfully"
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/candidates/{candidate_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_candidate_not_found(client):
    """Test deleting a non-existent candidate"""
    fake_id = str(uuid.uuid4())
    response = await client.delete(f"/api/v1/candidates/{fake_id}")
    
    assert response.status_code == 404
