import logging

from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore
from pymongo.errors import DuplicateKeyError

from coffee_backend.schemas.coffee import Coffee


class CoffeeCRUD:
    """CRUD class for coffee schema.
    Args:
        database(str): Name of the database to use for collection transactions.

    """

    def __init__(self, database: str) -> None:
        self.database = database

    async def create(
        self, coffee: Coffee, db_session: AsyncIOMotorClientSession
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
            await db_session.client[self.database]["coffee"].insert_one(
                document
            )
        except DuplicateKeyError:
            raise ValueError(  # pylint: disable=raise-missing-from
                "Unable to store entry in database due to key duplication"
            )
        logging.info("Stored new entry in database")
        logging.debug("Entry: %s", document)
        return coffee

    # async def read(self, coffee_id: UUID) -> Coffee:
    #     document = await self.collection.find_one({"_id": coffee_id})
    #     if document:
    #         return Coffee.parse_obj(document)
    #     else:
    #         return None

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

    # async def list(self) -> List[Coffee]:
    #     cursor = self.collection.find()
    #     documents = await cursor.to_list(length=None)
    #     return [Coffee.parse_obj(document) for document in documents]
