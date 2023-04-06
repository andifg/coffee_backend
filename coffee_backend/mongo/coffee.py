import json
import logging

from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore
from coffee_backend.schemas.coffee import Coffee


class CoffeeCRUD:
    def __init__(self, database: str) -> None:
        self.database = database

    async def create(
        self, coffee: Coffee, db_session: AsyncIOMotorClientSession
    ) -> Coffee:
        document = coffee.dict(by_alias=True)
        await db_session.client[self.database]["coffee"].insert_one(document)
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
