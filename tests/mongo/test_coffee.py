from uuid import UUID

import pytest

from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.schemas.coffee import Coffee
from tests.conftest import TestDBSessions


@pytest.mark.asyncio
async def test_mongo_create(
    init_mongo: TestDBSessions, dummy_coffee: Coffee, caplog: pytest.LogCaptureFixture
) -> None:
    """Test insert to mongodb.

    Args:
        init_mongo: Fixture for mongodb connections
    """

    dbname = "test_coffee_backend"

    test_crud = CoffeeCRUD(dbname)

    async with await init_mongo.asncy_session.start_session() as session:
        await test_crud.create(db_session=session, coffee=dummy_coffee)


    assert "Stored new entry in database" in caplog.messages
    assert f"Entry: {dummy_coffee.dict(by_alias=True)}" in caplog.messages


    with init_mongo.sync_probe_session.start_session() as session:
        result = list(session.client[dbname]["coffee"].find())
        assert len(result) == 1
        assert result[0] == {
            "_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
            "name": "Colombian",
            "ratings": [
                {
                    "_id": UUID("123e4367-e89b-12d3-a456-426655440000"),
                    "rating": 4,
                },
                {
                    "_id": UUID("123e4367-e49b-12d3-a456-426655440000"),
                    "rating": 2,
                },
                {
                    "_id": UUID("123e4367-e29b-12d3-a456-426655440000"),
                    "rating": 3,
                },
            ],
        }
