import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyDrinks, TestDBSessions


@pytest.mark.asyncio
async def test_delete_existing_drink(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting an existing drink record from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_drinks (DummyDrinks): Fixture providing dummy drink objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
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

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.delete(session, drink_1.id)

        assert result is True

    with init_mongo.sync_probe_session.start_session() as session:
        drinks_after_delete = list(
            session.client[settings.mongodb_database][
                settings.mongodb_drink_collection
            ].find()
        )
        assert len(drinks_after_delete) == 1
        assert drinks_after_delete[0] == drink_2.model_dump(by_alias=True)

    assert f"Deleted drink with id {drink_1.id}" in caplog.messages


@pytest.mark.asyncio
async def test_delete_nonexistent_drink(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting a non-existent drink record from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_drinks (DummyDrinks): Fixture providing dummy drink objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """

    unkown_id = uuid7()

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.delete(session, unkown_id)

    assert (
        str(not_found_error.value)
        == f"Drink with id {unkown_id} not found in collection"
    )
