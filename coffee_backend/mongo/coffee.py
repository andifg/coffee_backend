import logging
from typing import List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore
from pymongo.errors import DuplicateKeyError

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.schemas.coffee import Coffee
from coffee_backend.settings import settings


class CoffeeCRUD:
    """CRUD class for coffee schema.
    Args:
        database(str): Name of the database to use for collection transactions.

    """

    def __init__(self, database: str) -> None:
        self.database = database
        self.coffee_collection = settings.mongodb_coffee_collection

    async def create(
        self, db_session: AsyncIOMotorClientSession, coffee: Coffee
    ) -> Coffee:
        """Create a new coffee document in the database.

        Args:
            coffee (Coffee): The coffee document to insert.
            db_session (AsyncIOMotorClientSession): The database session.

        Returns:
            Coffee: The inserted coffee document.

        Raises:
            ValueError: If a key duplication error occurs when inserting the
                document.
        """
        document = coffee.dict(by_alias=True)
        try:
            await db_session.client[self.database][
                self.coffee_collection
            ].insert_one(document)
        except DuplicateKeyError:
            raise ValueError(  # pylint: disable=raise-missing-from
                "Unable to store entry in database due to key duplication"
            )
        logging.info("Stored new entry in database")
        logging.debug("Entry: %s", document)
        return coffee

    async def read_by_id(
        self, db_session: AsyncIOMotorClientSession, coffee_id: UUID
    ) -> Coffee:
        """
        Retrieves a document from the 'coffee' collection with the given ID.

        Args:
            db_session (AsyncIOMotorClientSession): The MongoDB client session.
            coffee_id (UUID): The ID of the coffee document to retrieve.

        Returns:
            Coffee: A `Coffee` instance representing the retrieved document.

        Raises:
            ObjectNotFoundError: If no document with the given ID is found.
        """
        document = await db_session.client[self.database][
            self.coffee_collection
        ].find_one({"_id": coffee_id})
        if document:
            logging.debug("Received entry from database")
            return Coffee.parse_obj(document)

        raise ObjectNotFoundError(f"Couldn't find entry for _id {coffee_id}")

    async def read_all(
        self, db_session: AsyncIOMotorClientSession
    ) -> List[Coffee]:
        """
        Retrieves all documents from the 'coffee' collection.

        Args:
            db_session (AsyncIOMotorClientSession): The MongoDB client session.

        Returns:
            List[Coffee]: A list of `Coffee` instances representing the
                          retrieved documents.

        Raises:
            ObjectNotFoundError: If the collection is empty.
        """
        cursor = db_session.client[self.database][self.coffee_collection].find()

        coffees = [
            Coffee.parse_obj(document)
            for document in await cursor.to_list(length=100)
        ]

        if len(coffees) == 0:
            raise ObjectNotFoundError(
                f"Collection {self.coffee_collection} is empty"
            )

        logging.debug("Received %s entries from database", len(coffees))
        return coffees

    # async def update(self, coffee_id: UUID, coffee: Coffee) -> Coffee:
    #     document = coffee.dict()
    #     result = await self.collection.update_one(
    #         {"_id": coffee_id}, {"$set": document}
    #     )
    #     if result.matched_count == 0:
    #         return None
    #     else:
    #         return coffee

    # async def delete(self, coffee_id: UUID) -> bool:
    #     result = await self.collection.delete_one({"_id": coffee_id})
    #     return result.deleted_count > 0
