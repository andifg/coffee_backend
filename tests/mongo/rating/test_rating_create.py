from uuid import UUID

import pytest

from coffee_backend.mongo.rating import RatingCRUD
from coffee_backend.settings import settings
from tests.conftest import DummyRatings, TestDBSessions


@pytest.mark.asyncio
async def test_mongo_rating_create(
    init_mongo: TestDBSessions,
    dummy_ratings: DummyRatings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test insert to mongodb.

    Args:
        init_mongo: Fixture for mongodb connections
    """

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    dummy_rating = dummy_ratings.rating_2

    async with await init_mongo.asncy_session.start_session() as session:
        await test_crud.create(db_session=session, rating=dummy_rating)

    assert "Stored new entry in database" in caplog.messages
    assert f"Entry: {dummy_rating.dict(by_alias=True)}" in caplog.messages

    with init_mongo.sync_probe_session.start_session() as session:
        result = list(
            session.client[settings.mongodb_database][
                settings.mongodb_rating_collection
            ].find()
        )
        assert len(result) == 1
        assert result[0] == {
            "_id": UUID("123e4567-e60b-12d3-a456-426655440000"),
            "rating": 4.5,
            "coffee_id": UUID("123e4567-e59b-12d3-a456-426655440000"),
        }


@pytest.mark.asyncio
async def test_mongo_coffee_create_duplicate(
    init_mongo: TestDBSessions, dummy_ratings: DummyRatings
) -> None:
    """Test inserting two items with the same _id raises a ValueError.

    Args:
        init_mongo: Fixture for MongoDB connections.
        dummy_ratings: Fixture that provides multiple dummy ratings objects
    """

    test_crud = RatingCRUD(
        settings.mongodb_database, settings.mongodb_rating_collection
    )

    with pytest.raises(ValueError) as value_error:
        async with await init_mongo.asncy_session.start_session() as session:
            await test_crud.create(
                db_session=session, rating=dummy_ratings.rating_2
            )
            await test_crud.create(
                db_session=session, rating=dummy_ratings.rating_2
            )

    assert (
        str(value_error.value)
        == "Unable to store entry in database due to key duplication"
    )
