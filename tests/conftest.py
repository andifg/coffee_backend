from dataclasses import dataclass
from typing import AsyncGenerator

import motor.motor_asyncio  # type: ignore
import pytest
import pytest_asyncio
from pymongo import MongoClient
from pytest_docker.plugin import Services  # type: ignore


@dataclass
class TestDBSessions:
    Async: motor.motor_asyncio.AsyncIOMotorClient
    Probe: MongoClient
    __test__: bool = False


@pytest_asyncio.fixture()
async def mongo_service(docker_ip: str, docker_services: Services) -> str:
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
    async_client = motor.motor_asyncio.AsyncIOMotorClient(
        mongo_service, serverSelectionTimeoutMS=5000
    )
    sync_client: MongoClient = MongoClient(mongo_service, serverSelectionTimeoutMS=5000)
    try:
        await async_client.server_info()
        yield TestDBSessions(async_client, sync_client)
        cleanup_db(sync_client)

    except Exception:
        print("Unable to connect to the server.")


def test_mongo(connection_string: str) -> bool:
    print("Try connection")
    client: MongoClient = MongoClient(connection_string)
    client.server_info()
    return True


def cleanup_db(db: MongoClient) -> None:
    db.drop_database("test_db")
    print("Cleaned up database between tests")
