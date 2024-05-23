import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from motor.core import AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.schemas.rating import Rating
from coffee_backend.settings import settings


class RatingCRUD:
    """CRUD class for rating schema.
    Args:
        database(str): Name of the database to use for collection transactions.

    """

    def __init__(self, database: str, rating_collection: str) -> None:
        self.database = database
        self.rating_collection = rating_collection
        self.first_rating = True

    async def create(
        self, db_session: AgnosticClientSession, rating: Rating
    ) -> Rating:
        """Create a new rating document in the database.

        Args:
            coffee (Coffee): The coffee document to insert.
            db_session (AgnosticClientSession): The database session.

        Returns:
            Coffee: The inserted coffee document.

        Raises:
            ValueError: If a key duplication error occurs when inserting the
                document.
        """
        document = rating.dict(by_alias=True)
        try:
            await db_session.client[self.database][
                self.rating_collection
            ].insert_one(document)

            if self.first_rating:
                logging.debug("Ensuring index for coffee_id attribute exists")
                await db_session.client[self.database][
                    self.rating_collection
                ].create_index("coffee_id")

                self.first_rating = False

        except DuplicateKeyError:
            raise ValueError(  # pylint: disable=raise-missing-from
                "Unable to store entry in database due to key duplication"
            )
        logging.info("Stored new entry in database")
        logging.debug("Entry: %s", document)
        return rating

    async def read(
        self,
        db_session: AgnosticClientSession,
        query: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
    ) -> List[Rating]:
        """Find ratings based on mongo search query.

        Args:
            db_session (AgnosticClientSession): The MongoDB client session.
            rating_id (UUID): The ID of the rating document to retrieve.
            max_results (int): max number of entries retrieved from db
            projection (Optional[Dict[str, int]]): Selection of columns to
                include or exclude in result.

        Returns:
            Rating: A `Rating` instance representing the retrieved document.
        """

        documents: List[Rating] = [
            doc
            async for doc in db_session.client[self.database][
                self.rating_collection
            ].find(filter=query, projection=projection)
        ]

        if documents:
            logging.debug("Received %s entries from database", len(documents))
            return [Rating.parse_obj(document) for document in documents]

        raise ObjectNotFoundError("Couldn't find entry for search query")

    async def update(
        self,
        db_session: AgnosticClientSession,
        rating_id: UUID,
        rating: Rating,
    ) -> Rating:
        """
        Updates the rating document with the specified ID in the database with
        the given rating data.

        Args:
            db_session (AgnosticClientSession): The MongoDB database
                  session to use.
            rating_id (UUID): The UUID of the rating document to update.
            rating (Rating): The new data to update the rating document with.

        Returns:
            Coffee: The updated rating document.

        Raises:
            ObjectNotFoundError: If no coffee document exists in the database
                with the specified ID.
            ValidationError: If the provided coffee data is invalid.
        """
        result = await db_session.client[self.database][
            self.rating_collection
        ].update_one(
            {"_id": rating_id},
            {"$set": rating.dict(by_alias=True, exclude={"id"})},
        )
        if result.matched_count == 0:
            raise ObjectNotFoundError(
                f"Rating with id {rating_id} not found in collection"
            )
        logging.info("Updated rating with id %s", rating_id)
        search_result = await self.read(
            db_session=db_session, query={"_id": rating_id}
        )
        updated_rating = search_result[0]
        logging.debug("Updated value: %s", updated_rating.json())
        return updated_rating

    async def delete(
        self,
        db_session: AgnosticClientSession,
        rating_id: UUID,
    ) -> bool:
        """Deletes a rating record from the database.

        Args:
            db_session (AgnosticClientSession): The database session to
                use for the operation.
            rating_id (UUID): The unique identifier of the rating to delete.

        Returns:
            bool: True if the coffee record was successfully deleted.

        Raises:
            ObjectNotFoundError: If the coffee with the specified ID is not
                found in the collection.
        """
        result = await db_session.client[self.database][
            self.rating_collection
        ].delete_one({"_id": rating_id})

        logging.info("Deleted rating with id %s", rating_id)

        if result.deleted_count != 1:
            raise ObjectNotFoundError(
                f"Rating with id {rating_id} not found in collection"
            )

        return True

    async def delete_many(
        self, db_session: AgnosticClientSession, query: dict[str, Any]
    ) -> bool:
        """Deletes multiple rating records from the database.

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
            self.rating_collection
        ].delete_many(query)

        logging.info("Deleted ratings for query %s", query)

        if result.deleted_count == 0:
            raise ObjectNotFoundError(f"No ratings found for query {query}")

        return True


rating_crud = RatingCRUD(
    database=settings.mongodb_database,
    rating_collection=settings.mongodb_rating_collection,
)
