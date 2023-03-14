import pytest

from tests.conftest import TestDBSessions


@pytest.mark.asyncio
async def test_mongo_insert(init_mongo: TestDBSessions) -> None:
    """Test insert to mongodb.

    Args:
        init_mongo: Fixture for mongodb connections
    """

    async with await init_mongo.asncy_session.start_session() as session:
        doc = {"_id": 123, "x": 1}
        await session.client["test_db"]["testcollection"].insert_one(doc)


@pytest.mark.asyncio
async def test_mongo_insert_two(init_mongo: TestDBSessions) -> None:
    """Second insert test to test db cleanup between tests.

    Args:
        init_mongo: Fixture for mongodb connections
    """
    async with await init_mongo.asncy_session.start_session() as session:
        doc = {"_id": 1234, "x": 1}
        await session.client["test_db"]["testcollection"].insert_one(doc)
