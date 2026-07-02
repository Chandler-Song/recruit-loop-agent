"""
Test configuration and fixtures
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.session import get_db
from app.main import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database session for each test"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    """Create a test client with overridden database dependency"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_position_data():
    """Sample position data for testing"""
    return {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "description": "Looking for an experienced backend developer",
        "location": "San Francisco, CA",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "search_keywords": ["backend", "python", "developer"],
        "loop_interval": 60
    }


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing"""
    return {
        "source": "github",
        "source_id": "12345",
        "github_login": "johndoe",
        "name": "John Doe",
        "email": "john@example.com",
        "location": "San Francisco, CA",
        "company": "Current Corp",
        "title": "Software Engineer",
        "bio": "Experienced Python developer",
        "followers": 100,
        "public_repos": 25,
        "skills": ["Python", "Django", "PostgreSQL"],
        "profile_url": "https://github.com/johndoe",
        "avatar_url": "https://github.com/johndoe.png",
        "search_keywords": ["python", "backend"]
    }


@pytest.fixture
def sample_pipeline_data():
    """Sample pipeline data for testing"""
    import uuid
    return {
        "position_id": str(uuid.uuid4()),
        "candidate_id": str(uuid.uuid4()),
        "status": "discovered",
        "score": 85.5,
        "contact_count": 0,
        "candidate_interest": "high",
        "notes": "Strong candidate"
    }
