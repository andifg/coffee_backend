from copy import deepcopy

import pytest
from faker import Faker
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.schemas import BrewingMethod, Drink
from coffee_backend.settings import settings
from tests.conftest import DummyDrinks, TestDBSessions


@pytest.mark.asyncio
async def test_delete_many_drinks_for_single_coffee(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting all drinks for an existing coffee record
        from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_drinks (DummyDrinks): Fixture providing dummy drink objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """
    drink_1 = dummy_drinks.drink_1
    drink_2 = dummy_drinks.drink_2

    fake = Faker()

    drink_3, drink_4, drink_5 = [
        Drink(
            _id=uuid7(),
            brewing_method=BrewingMethod.ESPRESSO,
            user_id=uuid7(),
            user_name=fake.name(),
            rating=4.5,
            coffee_bean_id=drink_1.coffee_bean_id,
        )
        for _ in range(3)
    ]

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_drink_collection
        ].insert_many(
            [
                drink_1.model_dump(by_alias=True),
                drink_2.model_dump(by_alias=True),
                drink_3.model_dump(by_alias=True),
                drink_4.model_dump(by_alias=True),
                drink_5.model_dump(by_alias=True),
            ]
        )

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.delete_many(
            session, {"coffee_bean_id": drink_1.coffee_bean_id}
        )

        assert result is True

    with init_mongo.sync_probe_session.start_session() as session:
        coffees_after_delete = list(
            session.client[settings.mongodb_database][
                settings.mongodb_drink_collection
            ].find()
        )
        assert len(coffees_after_delete) == 1
        assert coffees_after_delete[0] == drink_2.model_dump(by_alias=True)

    assert (
        f"Deleted drinks for query {{'coffee_bean_id': UUID('123e4567-e19b-12d3-a456-426655440000')}}"
        in caplog.messages
    )


@pytest.mark.asyncio
async def test_delete_many_non_existent_query(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting with a query that does not match to any drinks record.

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
            await test_crud.delete_many(session, {"coffee_id": unkown_id})

    assert (
        str(not_found_error.value)
        == f"No drinks found for query {{'coffee_id': UUID('{unkown_id}')}}"
    )
