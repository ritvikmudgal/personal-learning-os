"""SQLite database engine and session management.

Uses SQLAlchemy 2.0 async with aiosqlite driver.
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DATA_DIR, get_settings
from app.utils.logging import get_logger

logger = get_logger("db")

# Module-level engine and session factory (initialized lazily)
_engine = None
_session_factory = None


def _ensure_data_dir() -> None:
    """Create the data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_engine():
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        _ensure_data_dir()
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            # SQLite-specific: enable WAL mode for better concurrency
            connect_args={"check_same_thread": False},
        )
        logger.info("Database engine created: %s", settings.database_url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db_session() -> AsyncSession:
    """FastAPI dependency: yield an async database session.

    Usage in endpoints:
        async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize the database: create all tables.

    Called during application startup.
    """
    from app.db.models import Base  # noqa: avoid circular import

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


async def close_db() -> None:
    """Close the database engine. Called during application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine closed")
