from typing import Any, List
from uuid import UUID

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.schemas import Coffee
from coffee_backend.settings import settings
from tests.conftest import TestDBSessions


@pytest.mark.asyncio
async def test_mongo_coffee_aggregate_read(
    insert_coffees_with_matching_ratings: None,
    init_mongo: TestDBSessions,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test aggregate read from mongodb."""

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        pipeline: List[dict[str, Any]] = [
            {
                "$lookup": {
                    "from": "rating",
                    "localField": "_id",
                    "foreignField": "coffee_id",
                    "as": "rating",
                }
            },
            {
                "$addFields": {
                    "rating_count": {"$size": "$rating"},
                    "rating_average": {
                        "$round": [{"$avg": "$rating.rating"}, 2]
                    },
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "owner_id": 1,
                    "owner_name": 1,
                    "rating_count": 1,
                    "rating_average": 1,
                }
            },
            {"$limit": 10},
            {"$skip": 0},
        ]

        result = await test_crud.aggregate_read(
            db_session=session, pipeline=pipeline
        )

        assert result is not None

        assert result == [
            Coffee(
                _id=UUID("06635e36-cde9-7dd7-8000-d1ff37c420b1"),
                name="Test Coffee 1",
                owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                owner_name="Jdoe",
                rating_count=3,
                rating_average=3.17,
            ),
            Coffee(
                _id=UUID("06635e3c-40ce-7054-8000-30f4b778e7c9"),
                name="Test Coffee 2",
                owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                owner_name="Jdoe",
                rating_count=3,
                rating_average=2.0,
            ),
            Coffee(
                _id=UUID("06635e3f-4fb1-791d-8000-7fe0c420d735"),
                name="Test Coffee 3",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.5,
            ),
            Coffee(
                _id=UUID("06635e44-0cf5-788e-8000-58fedf8910c1"),
                name="Test Coffee 4",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.0,
            ),
            Coffee(
                _id=UUID("06635e44-8228-7b5c-8000-fde57ad84232"),
                name="Test Coffee 5",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.5,
            ),
        ]

        assert "Received 5 entries from database" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_coffee_aggregate_with_invalid_pipeline(
    insert_coffees_with_matching_ratings: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test aggregate read from mongodb with invalid pipeline."""

    async with await init_mongo.asncy_session.start_session() as session:
        pipeline = [
            {
                "$lookup": {
                    "fro": "rating",
                }
            },
        ]

        test_crud = CoffeeCRUD(
            settings.mongodb_database, settings.mongodb_coffee_collection
        )

        with pytest.raises(ValueError):
            await test_crud.aggregate_read(
                db_session=session, pipeline=pipeline
            )


@pytest.mark.asyncio
async def test_mongo_coffee_aggregate_with_empty_return(
    insert_coffees_with_matching_ratings: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test aggregate read from mongodb with empty return."""

    async with await init_mongo.asncy_session.start_session() as session:
        pipeline: List[dict[str, Any]] = [
            {"$match": {"_id": "Non existing id"}},
            {
                "$lookup": {
                    "from": "rating",
                    "localField": "_id",
                    "foreignField": "coffee_id",
                    "as": "rating",
                }
            },
            {
                "$addFields": {
                    "rating_count": {"$size": "$rating"},
                    "rating_average": {
                        "$round": [{"$avg": "$rating.rating"}, 2]
                    },
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "owner_id": 1,
                    "owner_name": 1,
                    "rating_count": 1,
                    "rating_average": 1,
                }
            },
            {"$limit": 10},
            {"$skip": 0},
        ]

        test_crud = CoffeeCRUD(
            settings.mongodb_database, settings.mongodb_coffee_collection
        )

        with pytest.raises(ObjectNotFoundError):
            await test_crud.aggregate_read(
                db_session=session, pipeline=pipeline
            )
