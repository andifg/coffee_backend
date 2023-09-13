from copy import deepcopy

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.rating import RatingCRUD
from coffee_backend.schemas.rating import Rating
from coffee_backend.settings import settings
from tests.conftest import DummyRatings, TestDBSessions


@pytest.mark.asyncio
async def test_delete_many_for_single_coffee(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting all ratings for an existing coffee record
        from the database.

    Args:
        init_mongo (TestDBSessions): Fixture for initializing the MongoDB test
            database.
        dummy_ratings (DummyRatings): Fixture providing dummy rating objects
            for testing.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """
    rating_1 = dummy_ratings.rating_1
    rating_2 = dummy_ratings.rating_2

    rating_3, rating_4, rating_5 = [
        Rating(_id=uuid7(), rating=4.5, coffee_id=rating_1.coffee_id)
        for _ in range(3)
    ]

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_rating_collection
        ].insert_many(
            [
                rating_1.dict(by_alias=True),
                rating_2.dict(by_alias=True),
                rating_3.dict(by_alias=True),
                rating_4.dict(by_alias=True),
                rating_5.dict(by_alias=True),
            ]
        )

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        result = await test_crud.delete_many(
            session, {"coffee_id": rating_1.coffee_id}
        )

        assert result is True

    with init_mongo.sync_probe_session.start_session() as session:
        coffees_after_delete = list(
            session.client[settings.mongodb_database][
                settings.mongodb_rating_collection
            ].find()
        )
        assert len(coffees_after_delete) == 1
        assert coffees_after_delete[0] == rating_2.dict(by_alias=True)

    assert (
        f"Deleted ratings for query {{'coffee_id': UUID('123e4567-e19b-12d3-a456-426655440000')}}"
        in caplog.messages
    )


@pytest.mark.asyncio
async def test_delete_many_non_existent_query(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test deleting with a query that does not match to any ratings record.

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
            await test_crud.delete_many(session, {"coffee_id": unkown_id})

    assert (
        str(not_found_error.value)
        == f"No ratings found for query {{'coffee_id': UUID('{unkown_id}')}}"
    )
