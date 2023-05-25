import copy
from uuid import uuid4

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyCoffees, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_coffee_update_rating(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test method to check the functionality of updating coffee rating in MongoDB.

    Args:
        init_mongo (TestDBSessions): A fixture to provide the MongoDB test
            database session.
        dummy_coffees (DummyCoffees): A fixture to provide dummy coffee data.
        caplog (pytest.LogCaptureFixture): A fixture to capture logs.
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
        result = await test_crud.update(session, coffee_2.id, coffee_1)

        coffee_1.id = coffee_2.id

        assert result == coffee_1

        assert f"Updated coffe with id {coffee_1.id}" in caplog.messages
        assert f"Updated value: {coffee_1.json()}" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_coffee_update_non_existing_coffee(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
) -> None:
    """Test updating a non-existing coffee in the MongoDB collection using
        CoffeeCRUD.update().

    Args:
        init_mongo: A fixture that sets up the test database connection.
        dummy_coffees: A fixture that provides dummy coffee objects for testing.


    Raises:
        ObjectNotFoundError: If the given coffee UUID does not exist in the
            database.

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

    non_existing_uuid = uuid4()

    with pytest.raises(ObjectNotFoundError) as not_found_error:

        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.update(
                db_session=session, coffee_id=non_existing_uuid, coffee=coffee_2
            )

    assert (
        str(not_found_error.value)
        == f"Coffee with id {non_existing_uuid} not found in collection"
    )


@pytest.mark.asyncio
async def test_mongo_coffee_update_verify_other_data_is_unchanged(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test that updating a coffee document in the MongoDB database using
    CoffeeCRUD.update() preserves other document fields that are not being
    updated.

    Args:
        init_mongo (TestDBSessions): A fixture that provides a MongoDB test
            session.
        dummy_coffees (DummyCoffees): A fixture that provides dummy coffee data
            for testing.
        caplog (pytest.LogCaptureFixture): A fixture that captures log messages
            during the test.
    """

    coffee_1 = dummy_coffees.coffee_1
    coffee_2 = dummy_coffees.coffee_2

    coffe_1_backup = copy.deepcopy(coffee_1)

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
        result = await test_crud.update(session, coffee_2.id, coffee_1)

        coffee_1.id = coffee_2.id

        assert result == coffee_1

        assert f"Updated coffe with id {coffee_1.id}" in caplog.messages
        assert f"Updated value: {coffee_1.json()}" in caplog.messages

    with init_mongo.sync_probe_session.start_session() as session:
        coffee_1_check = session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].find_one({"_id": coffe_1_backup.id})

        assert coffee_1_check == coffe_1_backup.dict(by_alias=True)
