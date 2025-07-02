import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_async_database_url(database_url: str) -> str:
    """
    Convierte un DATABASE_URL al formato asyncpg si es necesario.
    Esto hace que el código sea más tolerante a diferentes configuraciones.
    """
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Si ya tiene el driver asyncpg, lo devuelve tal como está
    if "+asyncpg" in database_url:
        return database_url
    
    # Si es postgresql:// sin driver, lo convierte a asyncpg
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Si es postgresql+psycopg2://, lo convierte a asyncpg
    if "+psycopg2" in database_url:
        return database_url.replace("+psycopg2", "+asyncpg")
    
    # Para otros casos, asume que necesita asyncpg
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://")
    
    return database_url

DATABASE_URL = get_async_database_url(os.getenv("DATABASE_URL", ""))

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