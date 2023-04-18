import pytest

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

    test_crud = CoffeeCRUD(settings.mongodb_database)

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.update(session, coffee_2.id, coffee_1)

        coffee_1.id = coffee_2.id

        assert result == coffee_1

        assert f"Updated coffe with id {coffee_1.id}" in caplog.messages
        assert f"Updated value: {coffee_1.json()}" in caplog.messages


# @pytest.mark.asyncio
# async def test_mongo_coffee_update_non_existing_coffee(
#     init_mongo: TestDBSessions,
#     dummy_coffees: DummyCoffees,
#     caplog: pytest.LogCaptureFixture,
# ) -> None:
#     pass


# @pytest.mark.asyncio
# async def test_mongo_coffee_update_verify_other_data_is_unchanged(
#     init_mongo: TestDBSessions,
#     dummy_coffees: DummyCoffees,
#     caplog: pytest.LogCaptureFixture,
# ) -> None:
#     pass
