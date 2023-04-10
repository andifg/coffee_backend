from uuid import UUID, uuid4

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
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

    test_crud = CoffeeCRUD(settings.mongodb_database)

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
            "ratings": [
                {
                    "_id": UUID("123e4367-e29b-12d3-a456-426655440000"),
                    "rating": 4,
                },
                {
                    "_id": UUID("123e4367-e39b-12d3-a456-426655440000"),
                    "rating": 2,
                },
                {
                    "_id": UUID("123e4367-e49b-12d3-a456-426655440000"),
                    "rating": 3,
                },
            ],
        }


@pytest.mark.asyncio
async def test_mongo_coffee_create_without_ratings(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test insert to mongodb.

    Args:
        init_mongo: Fixture for mongodb connections
        dummy_coffees: DummyCoffees,
        caplog: pytest.LogCaptureFixture,
    """

    test_crud = CoffeeCRUD(settings.mongodb_database)

    dummy_coffee = dummy_coffees.coffee_without_ratings

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
            "_id": UUID("123e4567-e99b-12d3-a456-426655440000"),
            "name": "Colombian",
            "ratings": [],
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

    test_crud = CoffeeCRUD(settings.mongodb_database)

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

    test_crud = CoffeeCRUD(settings.mongodb_database)

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

    test_crud = CoffeeCRUD(settings.mongodb_database)

    with pytest.raises(ObjectNotFoundError) as not_found_error:

        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.read_by_id(
                db_session=session, coffee_id=non_existing_uuid
            )

    assert (
        str(not_found_error.value)
        == f"Couldn't find entry for _id {non_existing_uuid}"
    )


@pytest.mark.asyncio
async def test_mongo_coffee_read_all_entries(
    init_mongo: TestDBSessions,
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test reading all items from the database.

    This function creates two Coffee instances, inserts them into the
    database, and then tests if the read_all method returns a list with the
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

    test_crud = CoffeeCRUD(settings.mongodb_database)

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.read_all(db_session=session)

        assert result == [coffee_1, coffee_2]

        assert "Received 2 entries from database" in caplog.messages

        assert len(result) == 2


@pytest.mark.asyncio
async def test_mongo_coffee_read_all_no_entries(
    init_mongo: TestDBSessions,
) -> None:
    """Test reading all items from an empty database.

    This function tests if the read_all method raises an ObjectNotFoundError
    exception when trying to read all items from an empty database.

    Args:
        init_mongo: Fixture for MongoDB connections.
    """

    test_crud = CoffeeCRUD(settings.mongodb_database)

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.read_all(db_session=session)

    assert (
        str(not_found_error.value)
        == f"Collection {settings.mongodb_coffee_collection} is empty"
    )
