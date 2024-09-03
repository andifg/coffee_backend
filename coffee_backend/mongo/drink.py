import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from motor.core import AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.schemas import Drink
from coffee_backend.settings import settings


class DrinkCRUD:
    """CRUD class for drink schema.
    Args:
        database(str): Name of the database to use for collection transactions.

    """

    def __init__(self, database: str, drink_collection: str) -> None:
        self.database = database
        self.drink_collection = drink_collection
        self.first_drink = True

    async def create(
        self, db_session: AgnosticClientSession, drink: Drink
    ) -> Drink:
        """Create a new drink document in the database.

        Args:
            coffee (Coffee): The coffee document to insert.
            db_session (AgnosticClientSession): The database session.

        Returns:
            Coffee: The inserted coffee document.

        Raises:
            ValueError: If a key duplication error occurs when inserting the
                document.
        """
        document = drink.model_dump(by_alias=True)
        try:
            await db_session.client[self.database][
                self.drink_collection
            ].insert_one(document)

            if self.first_drink:
                logging.debug("Ensuring index for coffee_id attribute exists")
                await db_session.client[self.database][
                    self.drink_collection
                ].create_index("coffee_id")

                self.first_drink = False

        except DuplicateKeyError:
            raise ValueError(  # pylint: disable=raise-missing-from
                "Unable to store entry in database due to key duplication"
            )
        logging.info("Stored new entry in database")
        logging.debug("Entry: %s", document)
        return drink

    async def read(
        self,
        db_session: AgnosticClientSession,
        query: Dict[str, Any],
        limit: int = 50,
        skip: int = 0,
        projection: Optional[Dict[str, int]] = None,
    ) -> List[Drink]:
        """Find drinks based on mongo search query.

        Args:
            db_session (AgnosticClientSession): The MongoDB client session.
            drink_id (UUID): The ID of the drink document to retrieve.
            max_results (int): max number of entries retrieved from db
            projection (Optional[Dict[str, int]]): Selection of columns to
                include or exclude in result.

        Returns:
            Drink: A `Drink` instance representing the retrieved document.
        """

        documents: List[Drink] = [
            doc
            async for doc in db_session.client[self.database][
                self.drink_collection
            ]
            .find(filter=query, projection=projection)
            .sort("_id", -1)
            .limit(limit)
            .skip(skip)
        ]

        if documents:
            logging.debug("Received %s entries from database", len(documents))
            return [Drink.model_validate(document) for document in documents]

        raise ObjectNotFoundError("Couldn't find entry for search query")

    async def update(
        self,
        db_session: AgnosticClientSession,
        drink_id: UUID,
        drink: Drink,
    ) -> Drink:
        """
        Updates the drink document with the specified ID in the database with
        the given drink data.

        Args:
            db_session (AgnosticClientSession): The MongoDB database
                  session to use.
            drink_id (UUID): The UUID of the drink document to update.
            drink (Drink): The new data to update the drink document with.

        Returns:
            Coffee: The updated drink document.

        Raises:
            ObjectNotFoundError: If no coffee document exists in the database
                with the specified ID.
            ValidationError: If the provided coffee data is invalid.
        """
        result = await db_session.client[self.database][
            self.drink_collection
        ].update_one(
            {"_id": drink_id},
            {"$set": drink.model_dump(by_alias=True, exclude={"id"})},
        )
        if result.matched_count == 0:
            raise ObjectNotFoundError(
                f"Drink with id {drink_id} not found in collection"
            )
        logging.info("Updated drink with id %s", drink_id)
        search_result = await self.read(
            db_session=db_session, query={"_id": drink_id}, limit=1, skip=0
        )
        updated_drink = search_result[0]
        logging.debug("Updated value: %s", updated_drink.model_dump_json())
        return updated_drink

    async def delete(
        self,
        db_session: AgnosticClientSession,
        drink_id: UUID,
    ) -> bool:
        """Deletes a drink record from the database.

        Args:
            db_session (AgnosticClientSession): The database session to
                use for the operation.
            drink_id (UUID): The unique identifier of the drink to delete.

        Returns:
            bool: True if the coffee record was successfully deleted.

        Raises:
            ObjectNotFoundError: If the coffee with the specified ID is not
                found in the collection.
        """
        result = await db_session.client[self.database][
            self.drink_collection
        ].delete_one({"_id": drink_id})

        logging.info("Deleted drink with id %s", drink_id)

        if result.deleted_count != 1:
            raise ObjectNotFoundError(
                f"Drink with id {drink_id} not found in collection"
            )

        return True

    async def delete_many(
        self, db_session: AgnosticClientSession, query: dict[str, Any]
    ) -> bool:
        """Deletes multiple drink records from the database.

        Args:
            db_session (AgnosticClientSession): The database session to
                use for the operation.
            query (str): The mongodb query.

        Returns:
            bool: True if the coffee records were successfully deleted.

        Raises:
            ObjectNotFoundError: If the coffee with the specified ID is not
                found in the collection.
        """
        result = await db_session.client[self.database][
            self.drink_collection
        ].delete_many(query)

        logging.info("Deleted drinks for query %s", query)

        if result.deleted_count == 0:
            raise ObjectNotFoundError(f"No drinks found for query {query}")

        return True


drink_crud = DrinkCRUD(
    database=settings.mongodb_database,
    drink_collection=settings.mongodb_drink_collection,
)
