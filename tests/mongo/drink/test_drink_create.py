from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyDrinks, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_drink_create(
    init_mongo: TestDBSessions,
    dummy_drinks: DummyDrinks,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test insert to mongodb.

    Args:
        init_mongo: Fixture for mongodb connections
    """

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    dummy_drink = dummy_drinks.drink_2

    async with await init_mongo.asncy_session.start_session() as session:
        await test_crud.create(db_session=session, drink=dummy_drink)

    assert "Stored new entry in database" in caplog.messages
    assert "Ensuring index for coffee_id attribute exists" in caplog.messages
    assert f"Entry: {dummy_drink.model_dump(by_alias=True)}" in caplog.messages

    assert test_crud.first_drink is False

    with init_mongo.sync_probe_session.start_session() as session:
        result = list(
            session.client[settings.mongodb_database][
                settings.mongodb_drink_collection
            ].find()
        )
        assert len(result) == 1
        assert result[0] == {
            "_id": UUID("123e4567-e60b-12d3-a456-426655440000"),
            "rating": 4.5,
            "brewing_method": None,
            "user_id": UUID("123e4567-e89b-12d3-a456-426655440000"),
            "user_name": "Berty",
            "coffee_bean_id": None,
            "image_exists": True,
            "coffee_bean_name": None,
            "coffee_bean_roasting_company": None,
        }


@pytest.mark.asyncio
async def test_mongo_drink_create_duplicate(
    init_mongo: TestDBSessions, dummy_drinks: DummyDrinks
) -> None:
    """Test inserting two items with the same _id raises a ValueError.

    Args:
        init_mongo: Fixture for MongoDB connections.
        dummy_drinks: Fixture that provides multiple dummy drinks objects
    """

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    with pytest.raises(ValueError) as value_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.create(
                db_session=session, drink=dummy_drinks.drink_2
            )
            await test_crud.create(
                db_session=session, drink=dummy_drinks.drink_2
            )

    assert (
        str(value_error.value)
        == "Unable to store entry in database due to key duplication"
    )


@pytest.mark.asyncio
async def test_mongo_drink_not_create_index_after_first_add(
    dummy_drinks: DummyDrinks,
) -> None:
    """Test that the index is not created after the first drink is added."""

    test_db_session = AsyncMock()

    insert_one_mock = AsyncMock()

    create_index_mock = AsyncMock()

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    test_db_session.client[settings.mongodb_database][
        settings.mongodb_drink_collection
    ].insert_one = insert_one_mock

    test_db_session.client[settings.mongodb_database][
        settings.mongodb_drink_collection
    ].create_index = create_index_mock

    test_crud.first_drink = False

    drink = await test_crud.create(
        db_session=test_db_session, drink=dummy_drinks.drink_2
    )

    assert drink == dummy_drinks.drink_2

    assert insert_one_mock.call_count == 1

    assert create_index_mock.call_count == 0
