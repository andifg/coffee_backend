import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyCoffees, TestDBSessions


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

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

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

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.read_all(db_session=session)

    assert (
        str(not_found_error.value)
        == f"Collection {settings.mongodb_coffee_collection} is empty"
    )
