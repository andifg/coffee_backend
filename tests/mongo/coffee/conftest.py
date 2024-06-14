from uuid import UUID

import pytest_asyncio

from coffee_backend.schemas import Coffee, Rating
from coffee_backend.settings import settings
from tests.conftest import TestDBSessions


@pytest_asyncio.fixture()
async def insert_coffees_with_matching_ratings(
    init_mongo: TestDBSessions,
) -> None:
    """Insert dummy coffees and ratings into the database.

    Create 3 dummy coffees with 3 ratings each.
    """

    dummy_coffees = [
        Coffee(
            _id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
            name="Test Coffee 1",
            roasting_company="Starbucks",
            owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            owner_name="Jdoe",
        ),
        Coffee(
            _id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
            name="Test Coffee 2",
            roasting_company="Starbucks",
            owner_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            owner_name="Jdoe",
        ),
        Coffee(
            _id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
            name="Test Coffee 3",
            roasting_company="Martermühle",
            owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            owner_name="Peter",
        ),
        Coffee(
            _id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
            name="Test Coffee 4",
            roasting_company="Martermühle",
            owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            owner_name="Peter",
        ),
        Coffee(
            _id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
            name="Test Coffee 5",
            roasting_company="Martermühle",
            owner_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            owner_name="Peter",
        ),
    ]

    dummy_ratings = [
        # Ratings for coffee 1
        Rating(
            _id=UUID("06635e4f-72e6-7516-8000-630b3d508193"),
            rating=4,
            coffee_id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
        ),
        Rating(
            _id=UUID("06635e50-f65b-70ab-8000-200f4cd71333"),
            rating=3.5,
            coffee_id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
        ),
        Rating(
            _id=UUID("06635e51-7cc3-785c-8000-fe9f5d2d5f77"),
            rating=2,
            coffee_id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
        ),
        # Dummy ratings for coffee 2
        Rating(
            _id=UUID("06635e55-87bd-7901-8000-12b10397feee"),
            rating=1,
            coffee_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
        ),
        Rating(
            _id=UUID("06635e56-568f-78d7-8000-4760d14251cd"),
            rating=2,
            coffee_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
        ),
        Rating(
            _id=UUID("06635e56-fbd6-7b54-8000-2ddb1b362019"),
            rating=3,
            coffee_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
        ),
        # Dummy ratings for coffee 3
        Rating(
            _id=UUID("06635e5a-dc8f-7db0-8000-d8df31352e12"),
            rating=5,
            coffee_id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
        ),
        Rating(
            _id=UUID("06635e5b-5db3-7cb3-8000-d62f02372924"),
            rating=4.5,
            coffee_id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
        ),
        Rating(
            _id=UUID("06635e5b-d1f9-7a49-8000-6f10e8376d7f"),
            rating=4,
            coffee_id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
        ),
        # Dummy ratings for coffee 4
        Rating(
            _id=UUID("06635e5f-b150-7b41-8000-cbf059c2f8f6"),
            rating=3.5,
            coffee_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
        ),
        Rating(
            _id=UUID("06635e60-3ba7-7221-8000-aca3d8f9c9ce"),
            rating=4,
            coffee_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
        ),
        Rating(
            _id=UUID("06635e60-c620-79fe-8000-5ed342f1b972"),
            rating=4.5,
            coffee_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
        ),
        # Dummy ratings for coffee 5
        Rating(
            _id=UUID("06635e62-fd4b-72c8-8000-de84ff1656c1"),
            rating=5,
            coffee_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
        ),
        Rating(
            _id=UUID("06635e63-b09f-7633-8000-e99ea17e1de8"),
            rating=4.5,
            coffee_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
        ),
        Rating(
            _id=UUID("06635e64-24c0-7e49-8000-7782743d4bb1"),
            rating=4,
            coffee_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
        ),
    ]

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [
                coffee.dict(by_alias=True, exclude_none=True)
                for coffee in dummy_coffees
            ]
        )

        session.client[settings.mongodb_database][
            settings.mongodb_rating_collection
        ].insert_many([rating.dict(by_alias=True) for rating in dummy_ratings])
