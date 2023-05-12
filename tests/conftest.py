import logging
from dataclasses import dataclass
from typing import AsyncGenerator
from uuid import UUID

import motor.motor_asyncio  # type: ignore
import pytest
import pytest_asyncio
from fastapi.datastructures import State
from httpx import AsyncClient
from pymongo import MongoClient
from pytest_docker.plugin import Services  # type: ignore

from coffee_backend.application import app, shutdown, startup
from coffee_backend.schemas.coffee import Coffee
from coffee_backend.schemas.rating import Rating
from coffee_backend.settings import settings

logging.basicConfig(level=logging.DEBUG)


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

    asncy_session: motor.motor_asyncio.AsyncIOMotorClient
    sync_probe_session: MongoClient
    __test__: bool = False


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
    coffee_without_ratings: Coffee


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


@pytest_asyncio.fixture()
async def init_mongo(mongo_service: str) -> AsyncGenerator:
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
        ratings=[
            Rating(_id=UUID("123e4367-e29b-12d3-a456-426655440000"), rating=4),
            Rating(_id=UUID("123e4367-e39b-12d3-a456-426655440000"), rating=2),
            Rating(_id=UUID("123e4367-e49b-12d3-a456-426655440000"), rating=3),
        ],
    )

    coffee_2 = Coffee(
        _id=UUID("123e4567-e59b-12d3-a456-426655440000"),
        name="Colombian",
        ratings=[
            Rating(_id=UUID("123e4367-e69b-12d3-a456-426655440000"), rating=4),
            Rating(_id=UUID("123e4367-e79b-12d3-a456-426655440000"), rating=2),
            Rating(_id=UUID("123e4367-e89b-12d3-a456-426655440000"), rating=3),
        ],
    )
    coffee_without_ratings = Coffee(
        _id=UUID("123e4567-e99b-12d3-a456-426655440000"),
        name="Colombian",
        ratings=[],
    )

    return DummyCoffees(
        coffee_1=coffee_1,
        coffee_2=coffee_2,
        coffee_without_ratings=coffee_without_ratings,
    )


@pytest_asyncio.fixture()
async def test_app(
    monkeypatch: pytest.MonkeyPatch,
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

    async with AsyncClient(app=app, base_url="https://test") as client:
        await startup()
        yield TestApp(app.state, client)
        await shutdown()


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
