from uuid import UUID

import pytest

from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyCoffees, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_coffee_create(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test insert to mongodb.

    Args:
        init_mongo: Fixture for mongodb connections
    """

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    dummy_coffee = dummy_coffees.coffee_1

    async with await init_mongo.asncy_session.start_session() as session:
        await test_crud.create(db_session=session, coffee=dummy_coffee)

    assert "Stored new entry in database" in caplog.messages
    assert f"Entry: {dummy_coffee.dict(by_alias=True)}" in caplog.messages

    with init_mongo.sync_probe_session.start_session() as session:
        result = list(
            session.client[settings.mongodb_database][
                settings.mongodb_coffee_collection
            ].find()
        )
        assert len(result) == 1
        assert result[0] == {
            "_id": UUID("123e4567-e19b-12d3-a456-426655440000"),
            "name": "Colombian",
            "owner_id": UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
            "owner_name": "Jdoe",
        }


@pytest.mark.asyncio
async def test_mongo_coffee_create_duplicate(
    init_mongo: TestDBSessions, dummy_coffees: DummyCoffees
) -> None:
    """Test inserting two items with the same _id raises a ValueError.

    Args:
        init_mongo: Fixture for MongoDB connections.
        dummy_coffee: Fixture that provides multiple dummy coffee objects
    """

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    with pytest.raises(ValueError) as value_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.create(
                db_session=session, coffee=dummy_coffees.coffee_1
            )
            await test_crud.create(
                db_session=session, coffee=dummy_coffees.coffee_1
            )

    assert (
        str(value_error.value)
        == "Unable to store entry in database due to key duplication"
    )
