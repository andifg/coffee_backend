from dataclasses import dataclass
from typing import AsyncGenerator

import motor.motor_asyncio  # type: ignore
import pytest_asyncio
from pymongo import MongoClient
from pytest_docker.plugin import Services  # type: ignore


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
        mongo_service, serverSelectionTimeoutMS=5000
    )
    sync_client: MongoClient = MongoClient(
        mongo_service, serverSelectionTimeoutMS=5000
    )
    try:
        await async_client.server_info()
        yield TestDBSessions(async_client, sync_client)
        cleanup_db(sync_client)

    except ConnectionError:
        print("Unable to connect to the server.")


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
    database.drop_database("test_db")
    print("Cleaned up database between tests")
