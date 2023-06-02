import logging
from typing import Any, Dict, List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore
from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo.errors import DuplicateKeyError

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.schemas.coffee import Coffee
from coffee_backend.settings import settings


class CoffeeCRUD:
    """CRUD class for coffee schema.
    Args:
        database(str): Name of the database to use for collection transactions.

    """

    def __init__(self, database: str, coffee_collection: str) -> None:
        self.database = database
        self.coffee_collection = coffee_collection

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

    async def find(
        self,
        db_session: AsyncIOMotorClientSession,
        query: Dict[str, Any],
        max_results: int = 100,
    ) -> List[Coffee]:
        """Find coffees based on mongo search query.

        Args:
            db_session (AsyncIOMotorClientSession): The MongoDB client session.
            coffee_id (UUID): The ID of the coffee document to retrieve.
            max_results (int): max number of entries retrieved from db

        Returns:
            Coffee: A `Coffee` instance representing the retrieved document.


        """

        cursor: AsyncIOMotorCursor = db_session.client[self.database][
            self.coffee_collection
        ].find(query)

        documents = await cursor.to_list(length=max_results)

        if documents:
            logging.debug("Received %s entries from database", len(documents))
            return [Coffee.parse_obj(document) for document in documents]

        raise ObjectNotFoundError("Couldn't find entry for search string")

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

    async def update(
        self,
        db_session: AsyncIOMotorClientSession,
        coffee_id: UUID,
        coffee: Coffee,
    ) -> Coffee:
        """
        Updates the coffee document with the specified ID in the database with
        the given coffee data.

        Args:
            db_session (AsyncIOMotorClientSession): The MongoDB database session
                to use.
            coffee_id (UUID): The UUID of the coffee document to update.
            coffee (Coffee): The new data to update the coffee document with.

        Returns:
            Coffee: The updated coffee document.

        Raises:
            ObjectNotFoundError: If no coffee document exists in the database
                with the specified ID.
            ValidationError: If the provided coffee data is invalid.
        """
        result = await db_session.client[self.database][
            self.coffee_collection
        ].update_one(
            {"_id": coffee_id},
            {"$set": coffee.dict(by_alias=True, exclude={"id"})},
        )
        if result.matched_count == 0:
            raise ObjectNotFoundError(
                f"Coffee with id {coffee_id} not found in collection"
            )
        logging.info("Updated coffe with id %s", coffee_id)
        updated_coffee = await self.read_by_id(
            db_session=db_session, coffee_id=coffee_id
        )
        logging.debug("Updated value: %s", updated_coffee.json())
        return updated_coffee

    async def delete(
        self,
        db_session: AsyncIOMotorClientSession,
        coffee_id: UUID,
    ) -> bool:
        """Deletes a coffee record from the database.

        Args:
            db_session (AsyncIOMotorClientSession): The database session to
                use for the operation.
            coffee_id (UUID): The unique identifier of the coffee to delete.

        Returns:
            bool: True if the coffee record was successfully deleted.

        Raises:
            ObjectNotFoundError: If the coffee with the specified ID is not
                found in the collection.
        """
        result = await db_session.client[self.database][
            self.coffee_collection
        ].delete_one({"_id": coffee_id})

        logging.info("Deleted coffe with id %s", coffee_id)

        if result.deleted_count != 1:
            raise ObjectNotFoundError(
                f"Coffee with id {coffee_id} not found in collection"
            )

        return True


coffee_crud = CoffeeCRUD(
    database=settings.mongodb_database,
    coffee_collection=settings.mongodb_coffee_collection,
)
