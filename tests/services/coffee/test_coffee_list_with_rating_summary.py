from unittest.mock import AsyncMock, MagicMock

import pytest
from uuid_extensions.uuid7 import uuid7

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.services.coffee import CoffeeService
from tests.conftest import DummyCoffees


@pytest.mark.asyncio
async def test_coffee_service_list_coffees_with_rating_summary(
    dummy_coffees: DummyCoffees,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test list_coffees_with_rating_summary method of CoffeeService."""
    coffee_1 = dummy_coffees.coffee_1
    coffee_2 = dummy_coffees.coffee_2

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.aggregate_read.return_value = [coffee_1, coffee_2]

    db_session_mock = AsyncMock()

    pipeline_aggregate_mock = MagicMock()
    pipeline_aggregate_mock.return_value = [{"$test": "test"}]

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    setattr(test_coffee_service, "_create_pipeline", pipeline_aggregate_mock)

    result = await test_coffee_service.list_coffees_with_rating_summary(
        db_session=db_session_mock
    )
    coffee_crud_mock.aggregate_read.assert_awaited_once_with(
        db_session=db_session_mock, pipeline=[{"$test": "test"}]
    )

    pipeline_aggregate_mock.assert_called_once_with(
        owner_id=None, page=1, page_size=10, first_id=None, search_query=None
    )

    assert result == [coffee_1, coffee_2]


@pytest.mark.asyncio
async def test_cof_serv_list_cof_with_rating_summary_empty_result() -> None:
    """Test list_coffees_with_rating_summary with empty response.

    Test that a HTTPException is raised when no coffees are found in the
    database

    """

    coffee_crud_mock = AsyncMock()
    coffee_crud_mock.aggregate_read.side_effect = ObjectNotFoundError(
        "Test message"
    )

    db_session_mock = AsyncMock()

    pipeline_aggregate_mock = MagicMock()
    pipeline_aggregate_mock.return_value = [{"$test": "test"}]

    test_coffee_service = CoffeeService(coffee_crud=coffee_crud_mock)

    setattr(test_coffee_service, "_create_pipeline", pipeline_aggregate_mock)

    result = await test_coffee_service.list_coffees_with_rating_summary(
        db_session=db_session_mock
    )

    assert result == []
    coffee_crud_mock.aggregate_read.assert_awaited_once_with(
        db_session=db_session_mock, pipeline=[{"$test": "test"}]
    )

    pipeline_aggregate_mock.assert_called_once_with(
        owner_id=None, page=1, page_size=10, first_id=None, search_query=None
    )


def test_coffee_service_pipeline_create_without_owner_id() -> None:
    """Pipeline should return a pipeline with correct skip and limit values."""
    test_coffee_service = CoffeeService(coffee_crud=AsyncMock())
    # pylint: disable=W0212
    result = test_coffee_service._create_pipeline(
        owner_id=None, page=1, page_size=10
    )
    # pylint: enable=W0212

    assert result == [
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
                "rating_average": {"$round": [{"$avg": "$rating.rating"}, 2]},
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

    # pylint: disable=W0212
    result_2 = test_coffee_service._create_pipeline(
        owner_id=None, page=2, page_size=20
    )

    # pylint: enable=W0212

    assert result_2 == [
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
                "rating_average": {"$round": [{"$avg": "$rating.rating"}, 2]},
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
        {"$limit": 40},
        {"$skip": 20},
    ]


def test_coffee_service_pipeline_create_with_owner_id() -> None:
    """Pipeline should return a pipeline with a match stage for the
    owner_id.
    """

    test_coffee_service = CoffeeService(coffee_crud=AsyncMock())

    owner_id = uuid7()
    # pylint: disable=W0212
    result = test_coffee_service._create_pipeline(
        owner_id=owner_id, page=1, page_size=10
    )
    # pylint: enable=W0212
    assert result == [
        {"$sort": {"_id": -1}},
        {"$match": {"owner_id": owner_id}},
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
                "rating_average": {"$round": [{"$avg": "$rating.rating"}, 2]},
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


def test_coffee_service_pipeline_create_with_first_id() -> None:
    """Pipeline should return a pipeline with a match stage for the
    first id.
    """

    test_coffee_service = CoffeeService(coffee_crud=AsyncMock())

    first_id = uuid7()
    # pylint: disable=W0212
    result = test_coffee_service._create_pipeline(
        owner_id=None, page=1, page_size=10, first_id=first_id
    )
    # pylint: enable=W0212
    assert result == [
        {"$sort": {"_id": -1}},
        {"$match": {"_id": {"$lte": first_id}}},
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
                "rating_average": {"$round": [{"$avg": "$rating.rating"}, 2]},
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


def test_coffee_service_pipeline_create_with_search_query() -> None:
    """Pipeline should return a pipeline with a match stage for the
    search query.
    """

    test_coffee_service = CoffeeService(coffee_crud=AsyncMock())

    search_query = "test"

    # pylint: disable=W0212
    result = test_coffee_service._create_pipeline(
        owner_id=None, page=1, page_size=10, search_query=search_query
    )
    # pylint: enable=W0212

    assert result == [
        {"$sort": {"_id": -1}},
        {
            "$match": {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {
                        "roasting_company": {
                            "$regex": search_query,
                            "$options": "i",
                        }
                    },
                    {"owner_name": {"$regex": search_query, "$options": "i"}},
                ]
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
                "rating_average": {"$round": [{"$avg": "$rating.rating"}, 2]},
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
