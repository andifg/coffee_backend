import uuid

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyCoffees, TestDBSessions


@pytest.mark.asyncio
async def test_delete_existing_coffee(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting an existing coffee record from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_coffees (DummyCoffees): Fixture providing dummy coffee objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """
    coffee_1 = dummy_coffees.coffee_1
    coffee_2 = dummy_coffees.coffee_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [coffee_1.dict(by_alias=True), coffee_2.dict(by_alias=True)]
        )

    test_crud = CoffeeCRUD(settings.mongodb_database)

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.delete(session, coffee_2.id)

        assert result is True

    with init_mongo.sync_probe_session.start_session() as session:
        coffees_after_delete = list(
            session.client[settings.mongodb_database][
                settings.mongodb_coffee_collection
            ].find()
        )
        assert len(coffees_after_delete) == 1
        assert coffees_after_delete[0] == coffee_1.dict(by_alias=True)

    assert f"Deleted coffe with id {coffee_2.id}" in caplog.messages


@pytest.mark.asyncio
async def test_delete_nonexistent_coffee(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting a non-existent coffee record from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_coffees (DummyCoffees): Fixture providing dummy coffee objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """

    unkown_id = uuid.uuid4()

    test_crud = CoffeeCRUD(settings.mongodb_database)

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.delete(session, unkown_id)

    assert (
        str(not_found_error.value)
        == f"Coffee with id {unkown_id} not found in collection"
    )
