import copy

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.rating import RatingCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyRatings, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_rating_update_rating(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test method to check the functionality of updating rating in MongoDB.

    Args:
        init_mongo (TestDBSessions): A fixture to provide the MongoDB test
            database session.
        dummy_ratings (DummyRatings): A fixture to provide dummy rating data.
        caplog (pytest.LogCaptureFixture): A fixture to capture logs.
    """

    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [
                rating_1.model_dump(by_alias=True),
                rating_2.model_dump(by_alias=True),
            ]
        )

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.update(session, rating_2.id, rating_1)

        rating_1.id = rating_2.id

        assert result == rating_1

        assert f"Updated rating with id {rating_1.id}" in caplog.messages
        assert f"Updated value: {rating_1.model_dump_json()}" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_rating_update_non_existing_rating(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
) -> None:
    """Test updating a non-existing rating in the MongoDB collection using
        RatingCRUD.update().

    Args:
        init_mongo: A fixture that sets up the test database connection.
        dummy_ratings: A fixture that provides dummy rating objects for testing.


    Raises:
        ObjectNotFoundError: If the given rating UUID does not exist in the
            database.

    """
    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_rating_collection
        ].insert_many(
            [
                rating_1.model_dump(by_alias=True),
                rating_2.model_dump(by_alias=True),
            ]
        )

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    non_existing_uuid = uuid7()

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.update(
                db_session=session, rating_id=non_existing_uuid, rating=rating_2
            )

    assert (
        str(not_found_error.value)
        == f"Rating with id {non_existing_uuid} not found in collection"
    )


@pytest.mark.asyncio
async def test_mongo_coffee_update_verify_other_data_is_unchanged(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
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

    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    rating_1_backup = copy.deepcopy(rating_1)

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_rating_collection
        ].insert_many(
            [
                rating_1.model_dump(by_alias=True),
                rating_2.model_dump(by_alias=True),
            ]
        )

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.update(session, rating_2.id, rating_1)

        rating_1.id = rating_2.id

        assert result == rating_1

        assert f"Updated rating with id {rating_1.id}" in caplog.messages
        assert f"Updated value: {rating_1.model_dump_json()}" in caplog.messages

    with init_mongo.sync_probe_session.start_session() as session:
        coffee_1_check = session.client[settings.mongodb_database][
            settings.mongodb_rating_collection
        ].find_one({"_id": rating_1_backup.id})

        assert coffee_1_check == rating_1_backup.model_dump(by_alias=True)
