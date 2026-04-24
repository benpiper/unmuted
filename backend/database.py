import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Default to unmuted.db in the backend directory
DB_PATH = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./unmuted.db")

engine = create_async_engine(
    DB_PATH,
    connect_args={"check_same_thread": False}, # Needed for SQLite
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    """Dependency for getting async database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
