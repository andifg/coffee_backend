import copy

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyDrinks, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_drink_update_drink(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test method to check the functionality of updating drink in MongoDB.

    Args:
        init_mongo (TestDBSessions): A fixture to provide the MongoDB test
            database session.
        dummy_drinks (DummyDrinks): A fixture to provide dummy drink data.
        caplog (pytest.LogCaptureFixture): A fixture to capture logs.
    """

    drink_1 = dummy_drinks.drink_1
    drink_2 = dummy_drinks.drink_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [
                drink_1.model_dump(by_alias=True),
                drink_2.model_dump(by_alias=True),
            ]
        )

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.update(session, drink_2.id, drink_1)

        drink_1.id = drink_2.id

        assert result == drink_1

        assert f"Updated drink with id {drink_1.id}" in caplog.messages
        assert f"Updated value: {drink_1.model_dump_json()}" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_drink_update_non_existing_drink(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
) -> None:
    """Test updating a non-existing drink in the MongoDB collection using
        DrinkCRUD.update().

    Args:
        init_mongo: A fixture that sets up the test database connection.
        dummy_drinks: A fixture that provides dummy drink objects for testing.


    Raises:
        ObjectNotFoundError: If the given drink UUID does not exist in the
            database.

    """
    drink_1 = dummy_drinks.drink_1
    drink_2 = dummy_drinks.drink_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_drink_collection
        ].insert_many(
            [
                drink_1.model_dump(by_alias=True),
                drink_2.model_dump(by_alias=True),
            ]
        )

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    non_existing_uuid = uuid7()

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.update(
                db_session=session, drink_id=non_existing_uuid, drink=drink_2
            )

    assert (
        str(not_found_error.value)
        == f"Drink with id {non_existing_uuid} not found in collection"
    )


@pytest.mark.asyncio
async def test_mongo_coffee_update_verify_other_data_is_unchanged(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
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

    drink_1 = dummy_drinks.drink_1
    drink_2 = dummy_drinks.drink_2

    drink_1_backup = copy.deepcopy(drink_1)

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_drink_collection
        ].insert_many(
            [
                drink_1.model_dump(by_alias=True),
                drink_2.model_dump(by_alias=True),
            ]
        )

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.update(session, drink_2.id, drink_1)

        drink_1.id = drink_2.id

        assert result == drink_1

        assert f"Updated drink with id {drink_1.id}" in caplog.messages
        assert f"Updated value: {drink_1.model_dump_json()}" in caplog.messages

    with init_mongo.sync_probe_session.start_session() as session:
        coffee_1_check = session.client[settings.mongodb_database][
            settings.mongodb_drink_collection
        ].find_one({"_id": drink_1_backup.id})

        assert coffee_1_check == drink_1_backup.model_dump(by_alias=True)
