import random

import pytest
from faker import Faker
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.schemas import BrewingMethod, Drink
from coffee_backend.settings import settings
from tests.conftest import DummyDrinks, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_drink_read_by_id(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Find a single drink by its id."""

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
        result = await test_crud.read(
            db_session=session, query={"_id": drink_1.id}
        )

        assert result == [drink_1]
        assert "Received 1 entries from database" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_drink_read_single_non_existing_id(
    init_mongo: TestDBSessions,
) -> None:
    """Test reading a single non-existing item by its _id.

    This function tests if the read_by_id method raises an ObjectNotFoundError
    exception when trying to read a non-existing item by its _id.

    Args:
        init_mongo: Fixture for MongoDB connections.
    """

    non_existing_uuid = uuid7()

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.read(
                db_session=session, query={"_id": non_existing_uuid}
            )

    assert str(not_found_error.value) == "Couldn't find entry for search query"


@pytest.mark.asyncio
async def test_mongo_drink_read_all_entries(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test reading all items from the database.

    This function creates two Rating instances, inserts them into the
    database, and then tests if the read method returns a list with the
    expected Rating instances.

    Args:
        init_mongo: Fixture for MongoDB connections.
        dummy_drinks: Fixture that provides multiple dummy drinks objects.
        caplog: Fixture that captures log output.
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
        result = await test_crud.read(db_session=session, query={})

        assert result == [drink_2, drink_1]

        assert "Received 2 entries from database" in caplog.messages

        assert len(result) == 2


@pytest.mark.asyncio
async def test_mongo_drink_read_by_coffee_id(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test to query multiple coffee ids from the crud read method."""

    drink_1 = dummy_drinks.drink_1
    drink_2 = dummy_drinks.drink_2
    equal_drink = uuid7()
    drink_1.coffee_bean_id = equal_drink
    drink_2.coffee_bean_id = equal_drink
    drink_3 = Drink(
        _id=uuid7(),
        coffee_bean_id=uuid7(),
        rating=5,
        brewing_method=BrewingMethod.AMERICANO,
        user_id=uuid7(),
        user_name="Robin Hood",
    )

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [
                drink_1.model_dump(by_alias=True),
                drink_2.model_dump(by_alias=True),
                drink_3.model_dump(by_alias=True),
            ]
        )

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.read(
            db_session=session,
            query={"coffee_bean_id": drink_1.coffee_bean_id},
        )

        assert result == [drink_2, drink_1]

        assert "Received 2 entries from database" in caplog.messages

        assert len(result) == 2


@pytest.mark.asyncio
async def test_mongo_drink_read_batch_tests(
    init_mongo: TestDBSessions,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure default ascending ordering by _id.

    Tests ensures that mongodb returns by default entries in ascending order by
    _id column.
    """

    faker = Faker()

    test_drinks = [
        Drink(
            _id=uuid7(),
            coffee_bean_id=uuid7(),
            brewing_method=random.choice(
                [
                    BrewingMethod.ESPRESSO,
                    BrewingMethod.CAPPUCCINO,
                    BrewingMethod.LATTE,
                    BrewingMethod.AMERICANO,
                    BrewingMethod.FILTER,
                    BrewingMethod.BIALETTI,
                ]
            ),
            user_id=uuid7(),
            user_name=faker.name(),
            rating=round(random.uniform(33.33, 66.66), 2),
        )
        for _ in range(random.randint(50, 100))
    ]

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_drink_collection
        ].insert_many(
            [drink.model_dump(by_alias=True) for drink in test_drinks]
        )

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.read(
            db_session=session,
            query={"_id": {"$in": [drink.id for drink in test_drinks[:50]]}},
        )

        assert len(result) == 50

        assert result == test_drinks[:50][::-1]

        assert "Received 50 entries from database" in caplog.messages
