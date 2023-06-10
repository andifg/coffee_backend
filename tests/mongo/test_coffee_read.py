import random

import pytest
from faker import Faker
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.schemas.coffee import Coffee
from coffee_backend.schemas.rating import Rating
from coffee_backend.settings import settings
from tests.conftest import DummyCoffees, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_coffee_read_by_id(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Find a single coffee by its id."""

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
        result = await test_crud.read(
            db_session=session, query={"_id": coffee_1.id}
        )

        assert result == [coffee_1]
        assert "Received 1 entries from database" in caplog.messages


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

    non_existing_uuid = uuid7()

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    with pytest.raises(ObjectNotFoundError) as not_found_error:

        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.read(
                db_session=session, query={"_id": non_existing_uuid}
            )

    assert str(not_found_error.value) == "Couldn't find entry for search query"


@pytest.mark.asyncio
async def test_mongo_coffee_read_all_entries(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test reading all items from the database.

    This function creates two Coffee instances, inserts them into the
    database, and then tests if the read method returns a list with the
    expected Coffee instances.

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
        result = await test_crud.read(db_session=session, query={})

        assert result == [coffee_1, coffee_2]

        assert "Received 2 entries from database" in caplog.messages

        assert len(result) == 2


@pytest.mark.asyncio
async def test_mongo_coffee_read_mutliple_entries_by_id(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test to query multiple coffee ids from the crud read method."""
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
        result = await test_crud.read(
            db_session=session,
            query={"_id": {"$in": [coffee_1.id, coffee_2.id]}},
        )

        assert result == [coffee_1, coffee_2]

        assert "Received 2 entries from database" in caplog.messages

        assert len(result) == 2


@pytest.mark.asyncio
async def test_mongo_coffee_read_by_name(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Find a single coffee by its name."""

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
        result = await test_crud.read(
            db_session=session, query={"name": coffee_1.name}
        )

        assert result == [coffee_1]
        assert "Received 1 entries from database" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_coffee_read_batch_tests(
    init_mongo: TestDBSessions,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure default ascending ordering by _id.

    Tests ensures that mongodb returns by default entries in ascending order by
    _id column.
    """

    faker = Faker()

    test_coffees = [
        Coffee(
            _id=uuid7(),
            name=faker.name(),
            ratings=[
                Rating(_id=uuid7(), rating=random.randint(0, 5))
                for _ in range(random.randint(0, 10))
            ],
        )
        for _ in range(random.randint(50, 100))
    ]

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many([coffee.dict(by_alias=True) for coffee in test_coffees])

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.read(
            db_session=session,
            query={"_id": {"$in": [coffee.id for coffee in test_coffees[:50]]}},
        )

        assert result == test_coffees[:50]

        assert "Received 50 entries from database" in caplog.messages

        assert len(result) == 50
