import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.rating import RatingCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyRatings, TestDBSessions


@pytest.mark.asyncio
async def test_delete_existing_rating(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting an existing coffee record from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_ratings (DummyRatings): Fixture providing dummy rating objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """
    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_rating_collection
        ].insert_many(
            [rating_1.dict(by_alias=True), rating_2.dict(by_alias=True)]
        )

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.delete(session, rating_1.id)

        assert result is True

    with init_mongo.sync_probe_session.start_session() as session:
        coffees_after_delete = list(
            session.client[settings.mongodb_database][
                settings.mongodb_rating_collection
            ].find()
        )
        assert len(coffees_after_delete) == 1
        assert coffees_after_delete[0] == rating_2.dict(by_alias=True)

    assert f"Deleted rating with id {rating_1.id}" in caplog.messages


@pytest.mark.asyncio
async def test_delete_nonexistent_rating(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting a non-existent rating record from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_ratings (DummyRatings): Fixture providing dummy rating objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """

    unkown_id = uuid7()

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    with pytest.raises(ObjectNotFoundError) as not_found_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.delete(session, unkown_id)

    assert (
        str(not_found_error.value)
        == f"Rating with id {unkown_id} not found in collection"
    )
