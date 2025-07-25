from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.declarative import declarative_base
from config import database_settings as settings
from sqlalchemy import MetaData

from utils.logger import CustomLogger

logger = CustomLogger(__name__)

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
async_engine = create_async_engine(DATABASE_URL, echo=True)
logger.info("Database connection established")
metadata = MetaData()

Base = declarative_base(metadata=metadata)

async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)
logger.info("Async session maker created")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        logger.info("Async session created")
        yield session
