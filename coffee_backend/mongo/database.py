import logging
from typing import AsyncGenerator

from fastapi import HTTPException, Request
from motor.core import AgnosticClient, AgnosticClientSession
from pymongo.errors import ServerSelectionTimeoutError


async def get_db(
    request: Request,
) -> AsyncGenerator[AgnosticClientSession, None]:
    """Obtains a database session for executing asynchronous MongoDB operations.

    Returns:
        AsyncGenerator[AgnosticClientSession, None]: An instance of the MongoDB
            client representing the database session.

    Raises:
        HTTPException: If there is a server selection timeout.

    """
    try:
        async_client: AgnosticClient = request.app.state.database_client
        async with await async_client.start_session() as db_session:
            yield db_session
    except ServerSelectionTimeoutError as error:
        logging.error("Unable to create database session: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Internal server error, please contact administrator",
        ) from error
