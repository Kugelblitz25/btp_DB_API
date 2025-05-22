"""Database configuration and session management for the application."""

import os
from typing import Optional, AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlmodel import SQLModel

load_dotenv(override=True)

# Database URL retrieved from environment variables.
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set.")

# SQLAlchemy engine for asynchronous database interaction.
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)

# SessionLocal is a factory for creating new AsyncSession instances.
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables() -> None:
    """
    Creates all database tables defined by SQLModel metadata.

    This function connects to the database using the engine and
    issues a command to create all tables if they don't already exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injector that provides a database session for a request.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with SessionLocal() as session:
        yield session
