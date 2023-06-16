import logging

import motor.motor_asyncio  # type: ignore
from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
from pymongo.errors import ServerSelectionTimeoutError


async def get_db(request: Request) -> motor.motor_asyncio.AsyncIOMotorClient:
    """Obtains a database session for executing asynchronous MongoDB operations.

    Returns:
        motor.motor_asyncio.AsyncIOMotorClient: An instance of the MongoDB
            client representing the database session.

    Raises:
        HTTPException: If there is a server selection timeout.

    """
    try:
        async_client: AsyncIOMotorClient = request.app.state.database_client
        async with await async_client.start_session() as db_session:
            yield db_session
    except ServerSelectionTimeoutError as error:
        logging.error("Unable to create database session: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Internal server error, please contact administrator",
        ) from error
