from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ASYNC_DB_URL = "postgresql://db:5432/postgres?user=postgres&password=postgres"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
async_session = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


async def get_db() -> Generator[AsyncSession, None, None]:
    async with async_session() as session:
        yield session