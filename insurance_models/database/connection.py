import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncSession:
    """Dependency to get a DB session."""
    async with AsyncSessionFactory() as session:
        yield session

async def init_db():
    """Initializes the database, creating tables if they don't exist."""
    # This is generally handled by Alembic migrations in a real application,
    # but can be useful for testing or simple setups.
    from .models import Base
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use with caution
        await conn.run_sync(Base.metadata.create_all)
