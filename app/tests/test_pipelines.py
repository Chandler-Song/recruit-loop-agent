"""
Pipelines API tests
"""
import pytest
import uuid


@pytest.mark.asyncio
async def test_create_pipeline(client, sample_position_data, sample_candidate_data):
    """Test creating a new pipeline"""
    # Create position and candidate first
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id,
        "status": "discovered",
        "score": 85.5,
        "contact_count": 0,
        "candidate_interest": "high",
        "notes": "Strong candidate"
    }
    
    response = await client.post("/api/v1/pipelines", json=pipeline_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["position_id"] == position_id
    assert data["candidate_id"] == candidate_id
    assert data["status"] == "discovered"
    assert data["score"] == 85.5
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_duplicate_pipeline(client, sample_position_data, sample_candidate_data):
    """Test creating a duplicate pipeline returns existing one"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id,
        "status": "discovered"
    }
    
    # Create first time
    response1 = await client.post("/api/v1/pipelines", json=pipeline_data)
    assert response1.status_code == 200
    pipeline_id_1 = response1.json()["id"]
    
    # Create duplicate
    response2 = await client.post("/api/v1/pipelines", json=pipeline_data)
    assert response2.status_code == 200
    pipeline_id_2 = response2.json()["id"]
    
    # Should return the same pipeline
    assert pipeline_id_1 == pipeline_id_2


@pytest.mark.asyncio
async def test_get_pipelines(client, sample_position_data, sample_candidate_data):
    """Test getting all pipelines"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id
    }
    await client.post("/api/v1/pipelines", json=pipeline_data)
    
    response = await client.get("/api/v1/pipelines")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_pipelines_with_pagination(client, sample_position_data, sample_candidate_data):
    """Test getting pipelines with pagination"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    # Create multiple candidates and pipelines
    for i in range(3):
        cand_data = sample_candidate_data.copy()
        cand_data["source_id"] = str(20000 + i)
        cand_data["github_login"] = f"pipeuser{i}"
        cand_response = await client.post("/api/v1/candidates", json=cand_data)
        candidate_id = cand_response.json()["id"]
        
        pipeline_data = {
            "position_id": position_id,
            "candidate_id": candidate_id
        }
        await client.post("/api/v1/pipelines", json=pipeline_data)
    
    response = await client.get("/api/v1/pipelines?skip=0&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_pipeline_by_id(client, sample_position_data, sample_candidate_data):
    """Test getting a specific pipeline by ID"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id
    }
    
    create_response = await client.post("/api/v1/pipelines", json=pipeline_data)
    pipeline_id = create_response.json()["id"]
    
    response = await client.get(f"/api/v1/pipelines/{pipeline_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pipeline_id


@pytest.mark.asyncio
async def test_get_pipeline_not_found(client):
    """Test getting a non-existent pipeline"""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/pipelines/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_pipeline(client, sample_position_data, sample_candidate_data):
    """Test updating a pipeline"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id
    }
    
    create_response = await client.post("/api/v1/pipelines", json=pipeline_data)
    pipeline_id = create_response.json()["id"]
    
    update_data = {"status": "contacted", "score": 90.0, "notes": "Updated notes"}
    response = await client.put(f"/api/v1/pipelines/{pipeline_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "contacted"
    assert data["score"] == 90.0
    assert data["notes"] == "Updated notes"


@pytest.mark.asyncio
async def test_update_pipeline_not_found(client):
    """Test updating a non-existent pipeline"""
    fake_id = str(uuid.uuid4())
    update_data = {"status": "contacted"}
    response = await client.put(f"/api/v1/pipelines/{fake_id}", json=update_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_pipeline_status(client, sample_position_data, sample_candidate_data):
    """Test updating pipeline status"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id
    }
    
    create_response = await client.post("/api/v1/pipelines", json=pipeline_data)
    pipeline_id = create_response.json()["id"]
    
    response = await client.put(f"/api/v1/pipelines/{pipeline_id}/status?status=interview")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interview"


@pytest.mark.asyncio
async def test_delete_pipeline(client, sample_position_data, sample_candidate_data):
    """Test deleting a pipeline"""
    pos_response = await client.post("/api/v1/positions", json=sample_position_data)
    position_id = pos_response.json()["id"]
    
    cand_response = await client.post("/api/v1/candidates", json=sample_candidate_data)
    candidate_id = cand_response.json()["id"]
    
    pipeline_data = {
        "position_id": position_id,
        "candidate_id": candidate_id
    }
    
    create_response = await client.post("/api/v1/pipelines", json=pipeline_data)
    pipeline_id = create_response.json()["id"]
    
    response = await client.delete(f"/api/v1/pipelines/{pipeline_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Pipeline deleted successfully"
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/pipelines/{pipeline_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_pipeline_not_found(client):
    """Test deleting a non-existent pipeline"""
    fake_id = str(uuid.uuid4())
    response = await client.delete(f"/api/v1/pipelines/{fake_id}")
    
    assert response.status_code == 404
