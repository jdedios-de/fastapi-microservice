from sqlmodel import SQLModel
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

# Create async engine
engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Create async session factory
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
