import logging

import motor.motor_asyncio  # type: ignore
from fastapi import HTTPException
from pymongo.errors import ServerSelectionTimeoutError

from coffee_backend.settings import settings

async_client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.mongodb_connetion_string,
    serverSelectionTimeoutMS=5000,
    uuidRepresentation="standard",
)


async def get_db() -> motor.motor_asyncio.AsyncIOMotorClient:
    """Obtains a database session for executing asynchronous MongoDB operations.

    Returns:
        motor.motor_asyncio.AsyncIOMotorClient: An instance of the MongoDB
            client representing the database session.

    Raises:
        HTTPException: If there is a server selection timeout.

    """
    try:
        async with await async_client.start_session() as db_session:
            yield db_session
    except ServerSelectionTimeoutError as error:
        logging.error(error)
        raise HTTPException(
            status_code=500,
            detail="Internal server error, please contact administrator",
        ) from error
