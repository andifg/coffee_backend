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
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test aggregate read from mongodb."""

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        pipeline: List[dict[str, Any]] = [
            {"$sort": {"_id": -1}},
            {
                "$lookup": {
                    "from": "drink",
                    "localField": "_id",
                    "foreignField": "coffee_bean_id",
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
                    "roasting_company": 1,
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
                _id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                name="Test Coffee 5",
                roasting_company="Martermühle",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.5,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                name="Test Coffee 4",
                roasting_company="Martermühle",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.0,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
                name="Test Coffee 3",
                roasting_company="Martermühle",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.5,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
                name="Test Coffee 2",
                roasting_company="Starbucks",
                owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                owner_name="Jdoe",
                rating_count=3,
                rating_average=2.0,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
                name="Test Coffee 1",
                roasting_company="Starbucks",
                owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                owner_name="Jdoe",
                rating_count=3,
                rating_average=3.17,
            ),
        ]

        assert "Received 5 entries from database" in caplog.messages


@pytest.mark.asyncio
async def test_mongo_coffee_aggregate_with_invalid_pipeline(
    insert_coffees_with_matching_drinks: None,
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
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test aggregate read from mongodb with empty return."""

    async with await init_mongo.asncy_session.start_session() as session:
        pipeline: List[dict[str, Any]] = [
            {"$match": {"_id": "Non existing id"}},
            {
                "$lookup": {
                    "from": "drink",
                    "localField": "_id",
                    "foreignField": "coffee_bean_id",
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


@pytest.mark.asyncio
async def test_mongo_coffee_aggregate_with_first_id(
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test aggregate read from mongodb with first_id parameter.

    Ensure that the first_id is used to only return coffees older than the
    first id. This is done by the $match stage in the pipeline.
    """

    test_crud = CoffeeCRUD(
        settings.mongodb_database, settings.mongodb_coffee_collection
    )

    async with await init_mongo.asncy_session.start_session() as session:
        pipeline: List[dict[str, Any]] = [
            {"$sort": {"_id": -1}},
            {
                "$match": {
                    "_id": {
                        "$lte": UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb")
                    }
                }
            },
            {
                "$lookup": {
                    "from": "drink",
                    "localField": "_id",
                    "foreignField": "coffee_bean_id",
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
                    "roasting_company": 1,
                    "owner_id": 1,
                    "owner_name": 1,
                    "rating_count": 1,
                    "rating_average": 1,
                }
            },
            {"$limit": 4},
            {"$skip": 0},
        ]

        result = await test_crud.aggregate_read(
            db_session=session, pipeline=pipeline
        )

        assert result is not None

        assert result == [
            Coffee(
                _id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                name="Test Coffee 4",
                roasting_company="Martermühle",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.0,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
                name="Test Coffee 3",
                roasting_company="Martermühle",
                owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
                owner_name="Peter",
                rating_count=3,
                rating_average=4.5,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
                name="Test Coffee 2",
                roasting_company="Starbucks",
                owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                owner_name="Jdoe",
                rating_count=3,
                rating_average=2.0,
            ),
            Coffee(
                _id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
                name="Test Coffee 1",
                roasting_company="Starbucks",
                owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                owner_name="Jdoe",
                rating_count=3,
                rating_average=3.17,
            ),
        ]

        assert "Received 4 entries from database" in caplog.messages
