import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Generator
from uuid import UUID

import motor.motor_asyncio  # type: ignore
import pytest
import pytest_asyncio
from fastapi import Request, UploadFile
from fastapi.datastructures import State
from httpx import AsyncClient
from motor.core import AgnosticClient
from pymongo import MongoClient
from pytest_docker.plugin import Services  # type: ignore
from starlette.datastructures import Headers

from coffee_backend.api import auth
from coffee_backend.application import app, lifespan
from coffee_backend.schemas import BrewingMethod, Coffee, Drink
from coffee_backend.settings import settings

logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger("faker")
logger.setLevel(logging.INFO)  # Quiet faker locale messages down in tests.

logger_urllib = logging.getLogger("urllib3")
logger_urllib.setLevel(
    logging.INFO
)  # Quiet urllib3 connection messages down in tests.


@dataclass
class TestDBSessions:
    """Wrapper for handing async session and sync probing session over to tests.

    Attributes:
        async_session: The async session that is also used within the full app.
            Therefore this is the session that is put under test to see wehther
            it is behaving exactly as expected with the ORM models of this
            project.
        sync_probe_session: An independent probe session that can be used for
            setting up the test environment prior the test execution itself or
            probing for an expected result after a test execution occured and
            the expected result should be asserted.
        __test__: Is set by default to enforce that pytest isn't picking up this
            class as a test suite that should be executed even though its name
            starts with "Test...".
    """

    asncy_session: AgnosticClient
    sync_probe_session: MongoClient
    __test__: bool = False


@dataclass
class DummyDrinks:
    """Wrapper for drink dummy objects.

    Attributes:
        drink_1 (Drink): Dummy drink instance with coffee_bean_id.
        drink_2 (Drink): Dummy drink without coffee_bean_id

    """

    drink_1: Drink
    drink_2: Drink


@dataclass
class DummyCoffees:
    """Wrapper for coffee dummy objects.

    Attributes:
        coffee_1 (Coffee): Dummy coffee instance with ratings.
        coffee_2 (Coffee): Another dummy coffee instance with ratings.
        coffee_without_ratings(Coffee): Dummy coffee without ratings.

    """

    coffee_1: Coffee
    coffee_2: Coffee


@dataclass
class DummyImages:
    """Wrapper for coffee images dummy objects.

    Attributes:
        image_1: UploadFile
        image_2: UploadFile
        image_1_bytes: bytes
        image_2_bytes: bytes

    """

    image_1: UploadFile
    image_1_bytes: bytes
    image_2: UploadFile
    image_2_bytes: bytes


@dataclass
class TestApp:
    """Wrapper for using an instance of the FastAPI app within tests.

    Attributes:
        state: The starlette state of the app for probing during tests.
        client: A httpx client running the FastAPI application under test.
        __test__: Is set by default to enforce that pytest isn't picking up this
            class as a test suite that should be executed even though its name
            starts with "Test...".
    """

    state: State
    client: AsyncClient
    __test__: bool = False


@pytest_asyncio.fixture(name="mongo_service")
async def fixture_mongo_service(
    docker_ip: str, docker_services: Services
) -> str:
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("mongo", 27017)
    connection_string = f"mongodb://root:example@{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: test_mongo(connection_string)
    )
    return connection_string


@pytest_asyncio.fixture(name="init_mongo")
async def setup_mongo_db(mongo_service: str) -> AsyncGenerator:
    """Create async and sync mongo db sessions for integration tests.

    Args:
        mongo_service: Fixture for checking availability of mongo db

    Yields:
        TestDBSessions object with sync and asnyc session
    """
    async_client = motor.motor_asyncio.AsyncIOMotorClient(
        mongo_service,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    sync_client: MongoClient = MongoClient(
        mongo_service,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    try:
        await async_client.server_info()
        yield TestDBSessions(async_client, sync_client)
        cleanup_db(sync_client)

    except ConnectionError:
        print("Unable to connect to the server.")


@pytest.fixture()
def dummy_coffees() -> DummyCoffees:
    """Fixture to provide dummy coffees for tests."""

    coffee_1 = Coffee(
        _id=UUID("123e4567-e19b-12d3-a456-426655440000"),
        name="Colombian",
        roasting_company="Starbucks",
        owner_id=UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        owner_name="Jdoe",
    )

    coffee_2 = Coffee(
        _id=UUID("123e4567-e59b-12d3-a456-426655440000"),
        name="Brazilian",
        roasting_company="Martermühle",
        owner_id=UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        owner_name="Jdoe",
    )

    return DummyCoffees(
        coffee_1=coffee_1,
        coffee_2=coffee_2,
    )


@pytest.fixture()
def dummy_drinks() -> DummyDrinks:
    """Fixture to provide dummy drinks for tests."""

    drink_1 = Drink(
        _id=UUID("123e4567-e20b-12d3-a456-426655440000"),
        rating=5,
        brewing_method=BrewingMethod.ESPRESSO,
        coffee_bean_id=UUID("123e4567-e19b-12d3-a456-426655440000"),
        user_id=UUID("018ee105-66b3-7f89-b6f3-807782e40350"),
        user_name="Jdoe",
        image_exists=False,
    )

    drink_2 = Drink(
        _id=UUID("123e4567-e60b-12d3-a456-426655440000"),
        rating=4.5,
        user_id=UUID("123e4567-e89b-12d3-a456-426655440000"),
        user_name="Berty",
        image_exists=True,
    )

    return DummyDrinks(drink_1=drink_1, drink_2=drink_2)


@pytest.fixture()
def dummy_coffee_images() -> Generator[DummyImages, None, None]:
    """Fixture to provide dummy coffee images for tests."""

    with open("tests/s3/testimages/coffee.jpeg", "rb") as image_1, open(
        "tests/s3/testimages/coffee2.jpeg", "rb"
    ) as image_2:
        upload_file_1 = UploadFile(
            file=image_1,
            filename="test_image_1.jpg",
            headers=Headers({"content-type": "image/jpeg"}),
        )
        upload_file_2 = UploadFile(
            file=image_2,
            filename="test_image_2.jpg",
            headers=Headers({"content-type": "image/jpeg"}),
        )

        image_1_bytes = image_1.read()
        image_2_bytes = image_2.read()
        image_1.seek(0, 0)
        image_2.seek(0, 0)

        yield DummyImages(
            image_1=upload_file_1,
            image_1_bytes=image_1_bytes,
            image_2=upload_file_2,
            image_2_bytes=image_2_bytes,
        )


@pytest_asyncio.fixture()
async def test_app(
    monkeypatch: pytest.MonkeyPatch, mongo_service: str
) -> AsyncGenerator[TestApp, None]:
    """Sets up an instance of the FastAPI application under test.

    Settings are mocked so that only test resources running within docker
    compose are used during test execution.

    Args:
        monkeypatch: The pytest monkeypatch to change settings to point to the
            test resources before the application is spun up.

    Returns:
        AsyncGenerator[TestApp, None]: A generator that is yielding the app
            under test and that ensures proper shutdown after test execution.
    """
    print("Setting up test app")

    monkeypatch.setattr(settings, "mongodb_database", "coffee_backend")
    monkeypatch.setattr(app.state, "mongodb_uri", mongo_service)

    async with AsyncClient(app=app, base_url="https://test") as client:
        async with lifespan(app):
            yield TestApp(app.state, client)


@pytest.fixture()
def mock_security_dependency() -> Generator[None, None, None]:
    """Fixture for mocking the security dependency during tests.

    This fixture sets up a mock security dependency by overriding the
    authentication verification function with a lambda that always returns True.
    This allows testing scenarios where authentication is always successful.

    """
    print("Setting up mock security dependency")

    app.dependency_overrides[auth.verify] = mock_user_token_payload

    yield

    print("Cleaning up mock security dependency")

    app.dependency_overrides = {}


def test_mongo(connection_string: str) -> bool:
    """Test if sync connection can be astablished.

    Args:
        connection_string: mongodb connection string

    Returns:
        Return true if no error occured
    """
    print("Try connection")
    client: MongoClient = MongoClient(connection_string)
    client.server_info()
    return True


def cleanup_db(database: MongoClient) -> None:
    """_summary_

    Args:
        db: MongoClient
    """
    database.drop_database(settings.mongodb_database)
    print("Cleaned up database between tests")


def mock_user_token_payload(request: Request) -> None:
    """For the purpose of testing, we mock the user token payload."""
    request.state.token = {
        "sub": "018ee105-66b3-7f89-b6f3-807782e40350",
        "family_name": "Black",
        "preferred_username": "Jdoe",
        "given_name": "John",
    }


@pytest_asyncio.fixture()
async def insert_coffees_with_matching_drinks(
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
        # Drinks for coffee 1
        Drink(
            _id=UUID("06635e4f-72e6-7516-8000-630b3d508193"),
            rating=4,
            brewing_method=BrewingMethod.ESPRESSO,
            user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            user_name="Jdoe",
            coffee_bean_id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
            image_exists=True,
        ),
        Drink(
            _id=UUID("06635e50-f65b-70ab-8000-200f4cd71333"),
            rating=3.5,
            brewing_method=BrewingMethod.FILTER,
            user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            user_name="Jdoe",
            coffee_bean_id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
            image_exists=True,
        ),
        Drink(
            _id=UUID("06635e51-7cc3-785c-8000-fe9f5d2d5f77"),
            rating=2,
            brewing_method=BrewingMethod.AMERICANO,
            user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            user_name="Jdoe",
            coffee_bean_id=UUID("0664ddeb-3b5d-73ba-8000-df8bd19c35bf"),
            image_exists=True,
        ),
        # Dummy ratings for coffee 2
        Drink(
            _id=UUID("06635e55-87bd-7901-8000-12b10397feee"),
            rating=1,
            brewing_method=BrewingMethod.ESPRESSO,
            user_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            user_name="Peter",
            coffee_bean_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e56-568f-78d7-8000-4760d14251cd"),
            rating=2,
            brewing_method=BrewingMethod.CAPPUCCINO,
            user_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            user_name="Peter",
            coffee_bean_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e56-fbd6-7b54-8000-2ddb1b362019"),
            rating=3,
            brewing_method=BrewingMethod.LATTE,
            user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
            user_name="Jane",
            coffee_bean_id=UUID("0664ddeb-3b5d-7e05-8000-bb6f99a750a7"),
            image_exists=False,
        ),
        # Dummy ratings for coffee 3
        Drink(
            _id=UUID("06635e5a-dc8f-7db0-8000-d8df31352e12"),
            rating=5,
            brewing_method=BrewingMethod.ESPRESSO,
            user_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            user_name="Peter",
            coffee_bean_id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
            image_exists=True,
        ),
        Drink(
            _id=UUID("06635e5b-5db3-7cb3-8000-d62f02372924"),
            rating=4.5,
            brewing_method=BrewingMethod.CAPPUCCINO,
            user_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            user_name="Peter",
            coffee_bean_id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e5b-d1f9-7a49-8000-6f10e8376d7f"),
            rating=4,
            brewing_method=BrewingMethod.LATTE,
            user_id=UUID("06635e42-a674-783c-8000-5647733a6497"),
            user_name="Peter",
            coffee_bean_id=UUID("0664ddeb-3b5d-7f76-8000-d5667ae65996"),
            image_exists=True,
        ),
        # Dummy ratings for coffee 4
        Drink(
            _id=UUID("06635e5f-b150-7b41-8000-cbf059c2f8f6"),
            rating=3.5,
            brewing_method=BrewingMethod.ESPRESSO,
            user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
            user_name="Jane",
            coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e60-3ba7-7221-8000-aca3d8f9c9ce"),
            rating=4,
            brewing_method=BrewingMethod.CAPPUCCINO,
            user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
            user_name="Jane",
            coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e60-c620-79fe-8000-5ed342f1b972"),
            rating=4.5,
            brewing_method=BrewingMethod.LATTE,
            user_id=UUID("066656b9-479d-7a27-8000-dfecb56faf1a"),
            user_name="Jane",
            coffee_bean_id=UUID("0664ddeb-3b5e-7093-8000-fb7c6d7c12fb"),
            image_exists=True,
        ),
        # Dummy ratings for coffee 5
        Drink(
            _id=UUID("06635e62-fd4b-72c8-8000-de84ff1656c1"),
            rating=5,
            brewing_method=BrewingMethod.AMERICANO,
            user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            user_name="Jdoe",
            coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e63-b09f-7633-8000-e99ea17e1de8"),
            rating=4.5,
            brewing_method=BrewingMethod.AMERICANO,
            user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            user_name="Jdoe",
            coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
            image_exists=False,
        ),
        Drink(
            _id=UUID("06635e64-24c0-7e49-8000-7782743d4bb1"),
            rating=4,
            brewing_method=BrewingMethod.ESPRESSO,
            user_id=UUID("06635e3d-7741-755d-8000-64c83f422732"),
            user_name="Jdoe",
            coffee_bean_id=UUID("0664ddeb-3b5e-716d-8000-907336604f50"),
            image_exists=True,
        ),
    ]

    with init_mongo.sync_probe_session.start_session() as session:
        session.client[settings.mongodb_database][
            settings.mongodb_coffee_collection
        ].insert_many(
            [
                coffee.model_dump(by_alias=True, exclude_none=True)
                for coffee in dummy_coffees
            ]
        )

        session.client[settings.mongodb_database][
            settings.mongodb_drink_collection
        ].insert_many(
            [rating.model_dump(by_alias=True) for rating in dummy_ratings]
        )
