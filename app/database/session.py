from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Create async database engine
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Set to True for SQL query logging in debug mode
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session maker
from sqlalchemy.orm import sessionmaker
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        yield session