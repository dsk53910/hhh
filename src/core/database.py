"""
Database service for HHH Bot
Handles async database operations and connection management
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import logging

from src.models.database import Base
from src.utils import get_logger


logger = get_logger(__name__)


class DatabaseService:
    """Async database service with connection pooling and lifecycle management"""

    def __init__(self, database_url: str, echo: bool = False, pool_size: int = 10):
        self.database_url = database_url
        self.echo = echo
        self.pool_size = pool_size

        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
        )

        # Create async session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self):
        """Create all database tables"""
        logger.info("creating_database_tables")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created")

    async def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        logger.warning("dropping_database_tables")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("database_tables_dropped")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session (context manager)"""
        async with self.async_session() as session:
            try:
                yield session
            except Exception as e:
                logger.error("database_session_error: %s", str(e), exc_info=True)
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.debug("database_health_check_passed")
            return True
        except Exception as e:
            logger.error("database_health_check_failed: %s", str(e), exc_info=True)
            return False

    async def close(self):
        """Close all database connections"""
        logger.info("closing_database_connections")
        await self.engine.dispose()
        logger.info("database_connections_closed")


# Global database service instance
db_service: Optional[DatabaseService] = None


def get_database_service(
    database_url: str,
    echo: bool = False,
    pool_size: int = 10,
) -> DatabaseService:
    """
    Get or create database service instance

    Args:
        database_url: Database connection URL
        echo: Whether to log SQL queries
        pool_size: Connection pool size

    Returns:
        DatabaseService instance
    """
    global db_service
    if db_service is None:
        db_service = DatabaseService(database_url, echo, pool_size)
        logger.info("database_service_created: %s", database_url)
    return db_service


def get_db_service() -> Optional[DatabaseService]:
    """Get global database service instance"""
    return db_service


async def init_database(
    database_url: str, echo: bool = False, pool_size: int = 10
) -> DatabaseService:
    """
    Initialize database service and create tables

    Args:
        database_url: Database connection URL
        echo: Whether to log SQL queries
        pool_size: Connection pool size

    Returns:
        Initialized DatabaseService instance
    """
    service = get_database_service(database_url, echo, pool_size)

    # Test connection
    if not await service.health_check():
        raise ConnectionError("Database connection failed")

    # Create tables if they don't exist
    await service.create_tables()

    logger.info("database_initialized")
    return service


# Database context manager for dependency injection
async def get_db_session():
    """Get database session for dependency injection"""
    service = get_db_service()
    if not service:
        raise RuntimeError("Database service not initialized")

    async for session in service.get_session():
        yield session


# Database utility functions
async def with_db_session(func):
    """Decorator to provide database session to async function"""

    async def wrapper(*args, **kwargs):
        service = get_db_service()
        if not service:
            raise RuntimeError("Database service not initialized")

        async for session in service.get_session():
            return await func(session, *args, **kwargs)

    return wrapper


class DatabaseTransaction:
    """Helper class for transaction management"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.is_committed = False

    async def commit(self):
        """Commit transaction"""
        await self.session.commit()
        self.is_committed = True
        logger.debug("database_transaction_committed")

    async def rollback(self):
        """Rollback transaction"""
        if not self.is_committed:
            await self.session.rollback()
            logger.debug("database_transaction_rolled_back")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()


def transaction(session: AsyncSession) -> DatabaseTransaction:
    """Create transaction context manager"""
    return DatabaseTransaction(session)
