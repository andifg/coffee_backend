from uuid import uuid4

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyCoffees, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_coffee_read_single_id(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test reading a single item by its _id.

    This function creates two Coffee instances, inserts them into the
    database, and then tests if the read_by_id method returns the expected
    result for the first Coffee instance.

    Args:
        init_mongo: Fixture for MongoDB connections.
        dummy_coffee: Fixture that provides multiple dummy coffee objects.
        caplog: Fixture that captures log output.
    """

    coffee_1 = dummy_coffees.coffee_1
    coffee_2 = dummy_coffees.coffee_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [coffee_1.dict(by_alias=True), coffee_2.dict(by_alias=True)]
        )

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.read_by_id(
            db_session=session, coffee_id=coffee_1.id
        )

        assert result == coffee_1

        assert "Received entry from database" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_coffee_read_single_non_existing_id(
    init_mongo: TestDBSessions,
) -> None:
    """Test reading a single non-existing item by its _id.

    This function tests if the read_by_id method raises an ObjectNotFoundError
    exception when trying to read a non-existing item by its _id.

    Args:
        init_mongo: Fixture for MongoDB connections.
    """

    non_existing_uuid = uuid4()

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    with pytest.raises(ObjectNotFoundError) as not_found_error:

        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.read_by_id(
                db_session=session, coffee_id=non_existing_uuid
            )

    assert (
        str(not_found_error.value)
        == f"Couldn't find entry for _id {non_existing_uuid}"
    )
