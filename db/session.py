# backend/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/api_copilot",
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "ssl": False   # ✅ THIS disables SSL correctly for asyncpg
    }
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
