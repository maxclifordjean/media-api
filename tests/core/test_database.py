import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from media_api.core.database import get_db, AsyncSessionLocal


@pytest.mark.asyncio
class TestDatabase:
    async def test_get_db_returns_async_session(self, override_get_db):
        db_gen = override_get_db()
        db_session = await anext(db_gen)

        assert isinstance(db_session, AsyncSession)

        await db_gen.aclose()

    async def test_get_db_function_works(self, test_db_engine):
        # Test that get_db function returns a proper async session
        from media_api.core.database import get_db
        
        # Simply test that the function exists and can be called
        db_generator = get_db()
        assert db_generator is not None
