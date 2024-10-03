from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.schemas import BrewingMethod, Drink
from coffee_backend.services.drink import DrinkService
from coffee_backend.settings import settings
from tests.conftest import TestDBSessions


@pytest.mark.asyncio
async def test_drink_service_list_drinks_with_coffee_bean_information(
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test list_drinks_with_coffee_bean_information with no filters."""

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    test_service = DrinkService(
        drink_crud=test_crud,
    )

    async with await init_mongo.asncy_session.start_session() as session:

        result = await test_service.list_drinks_with_coffee_bean_information(
            db_session=session, page_size=5, page=1
        )
        assert len(result) == 5

        assert result == [
            Drink(
                _id=UUID("06635e64-24c0-7e49-8000-7782743d4bb1"),
                brewing_method=BrewingMethod.ESPRESSO,
                rating=4.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=True,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e63-b09f-7633-8000-e99ea17e1de8"),
                brewing_method=BrewingMethod.AMERICANO,
                rating=4.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=False,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e62-fd4b-72c8-8000-de84ff1656c1"),
                brewing_method=BrewingMethod.AMERICANO,
                rating=5.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=False,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e60-c620-79fe-8000-5ed342f1b972"),
                brewing_method=BrewingMethod.LATTE,
                rating=4.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=True,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e60-3ba7-7221-8000-aca3d8f9c9ce"),
                brewing_method=BrewingMethod.CAPPUCCINO,
                rating=4.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=False,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
        ]


@pytest.mark.asyncio
async def test_drink_service_list_drinks_with_coffee_bean_information_first_id_(
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test list_drinks_with_coffee_bean_information with first_id filter."""

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    test_service = DrinkService(
        drink_crud=test_crud,
    )

    async with await init_mongo.asncy_session.start_session() as session:

        result = await test_service.list_drinks_with_coffee_bean_information(
            db_session=session,
            page_size=5,
            page=1,
            first_id=UUID("06635e63-b09f-7633-8000-e99ea17e1de8"),
        )
        assert len(result) == 5

        assert result == [
            Drink(
                _id=UUID("06635e63-b09f-7633-8000-e99ea17e1de8"),
                brewing_method=BrewingMethod.AMERICANO,
                rating=4.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=False,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e62-fd4b-72c8-8000-de84ff1656c1"),
                brewing_method=BrewingMethod.AMERICANO,
                rating=5.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=False,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e60-c620-79fe-8000-5ed342f1b972"),
                brewing_method=BrewingMethod.LATTE,
                rating=4.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=True,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e60-3ba7-7221-8000-aca3d8f9c9ce"),
                brewing_method=BrewingMethod.CAPPUCCINO,
                rating=4.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=False,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e5f-b150-7b41-8000-cbf059c2f8f6"),
                brewing_method=BrewingMethod.ESPRESSO,
                rating=3.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=False,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
        ]


@pytest.mark.asyncio
async def test_drink_service_list_drinks_with_coffee_bean_coffee_bean_filter(
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test list_drinks_with_coffee_bean_information with coffee_bean_id
    filter."""

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    test_service = DrinkService(
        drink_crud=test_crud,
    )

    async with await init_mongo.asncy_session.start_session() as session:

        result = await test_service.list_drinks_with_coffee_bean_information(
            db_session=session,
            page_size=5,
            page=1,
            coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
        )
        assert len(result) == 3

        assert result == [
            Drink(
                _id=UUID("06635e64-24c0-7e49-8000-7782743d4bb1"),
                brewing_method=BrewingMethod.ESPRESSO,
                rating=4.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=True,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e63-b09f-7633-8000-e99ea17e1de8"),
                brewing_method=BrewingMethod.AMERICANO,
                rating=4.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=False,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e62-fd4b-72c8-8000-de84ff1656c1"),
                brewing_method=BrewingMethod.AMERICANO,
                rating=5.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
                user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
                user_name="Jdoe",
                image_exists=False,
                coffee_bean_name="Test Coffee 5",
                coffee_bean_roasting_company="Martermühle",
            ),
        ]


@pytest.mark.asyncio
async def test_drink_service_list_drinks_with_coffee_bean_information_user(
    insert_coffees_with_matching_drinks: None,
    init_mongo: TestDBSessions,
) -> None:
    """Test list_drinks_with_coffee_bean_information with user filter."""

    test_crud = DrinkCRUD(
        settings.mongodb_database, settings.mongodb_drink_collection
    )

    test_service = DrinkService(
        drink_crud=test_crud,
    )

    async with await init_mongo.asncy_session.start_session() as session:

        result = await test_service.list_drinks_with_coffee_bean_information(
            db_session=session,
            page_size=5,
            page=1,
            user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
        )
        assert len(result) == 4

        assert result == [
            Drink(
                _id=UUID("06635e60-c620-79fe-8000-5ed342f1b972"),
                brewing_method=BrewingMethod.LATTE,
                rating=4.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=True,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e60-3ba7-7221-8000-aca3d8f9c9ce"),
                brewing_method=BrewingMethod.CAPPUCCINO,
                rating=4.0,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=False,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e5f-b150-7b41-8000-cbf059c2f8f6"),
                brewing_method=BrewingMethod.ESPRESSO,
                rating=3.5,
                coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=False,
                coffee_bean_name="Test Coffee 4",
                coffee_bean_roasting_company="Martermühle",
            ),
            Drink(
                _id=UUID("06635e56-fbd6-7b54-8000-2ddb1b362019"),
                brewing_method=BrewingMethod.LATTE,
                rating=3.0,
                coffee_bean_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
                user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
                user_name="Jane",
                image_exists=False,
                coffee_bean_name="Test Coffee 2",
                coffee_bean_roasting_company="Starbucks",
            ),
        ]


@pytest.mark.asyncio
async def test_drink_service_list_drinks_with_coffee_bean_empty_db_response(
    insert_coffees_with_matching_drinks: None,
) -> None:
    """Test list_drinks_with_coffee_bean_information with empty database
    response."""

    db_session_mock = AsyncMock()

    drink_crud_mock = AsyncMock()
    drink_crud_mock.aggregate_read.side_effect = ObjectNotFoundError(
        "Test message"
    )

    test_drink_service = DrinkService(drink_crud=drink_crud_mock)

    result = await test_drink_service.list_drinks_with_coffee_bean_information(
        db_session=db_session_mock, page_size=5, page=1
    )

    assert result == []
