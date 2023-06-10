import logging
from typing import List

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.mongo.coffee import coffee_crud as coffee_crud_instance
from coffee_backend.schemas.coffee import Coffee


class CoffeeService:
    """Service layer between API and CRUD layer for handling coffee-related
    operations.
    """

    def __init__(self, coffee_crud: CoffeeCRUD):
        """
        Initializes a new instance of the CoffeeService class.

        Args:
            coffee_crud (CoffeeCRUD): An instance of the CoffeeCRUD class for
            performing CRUD operations.
        """
        self.coffee_crud = coffee_crud

    async def add_coffee(
        self, db_session: AsyncIOMotorClientSession, coffee: Coffee
    ) -> Coffee:
        """
        Adds a new coffee to the database.

        Check whether name is already existing. If not create new coffee object.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.
            coffee (Coffee): The coffee object to be added.

        Returns:
            Coffee: The added coffee object.

        Raises:
            Exception: If an error occurs while creating the coffee.
        """
        try:
            await self.coffee_crud.read(
                db_session=db_session, query={"name": coffee.name}
            )
        except ObjectNotFoundError:
            return await self.coffee_crud.create(
                coffee=coffee, db_session=db_session
            )

        logging.debug(
            "Coffee with id %s will not get created due to name %s"
            " already existing",
            coffee.id,
            coffee.name,
        )
        raise HTTPException(
            status_code=400, detail="Coffee name is already existing"
        )

    async def list(self, db_session: AsyncIOMotorClientSession) -> List[Coffee]:
        """Retrieve a list of coffee objects from the database.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.

        Returns:
            List[Coffee]: A list of coffee objects retrieved from the crud
                class.

        """
        return await self.coffee_crud.read(db_session=db_session, query={})


#     def get_coffee(self, coffee_id):q
#         return self.coffee_crud.read(coffee_id)

#     def update_coffee(self, coffee_id, updated_coffee):
#         self.coffee_crud.update(coffee_id, updated_coffee)

#     def delete_coffee(self, coffee_id):
#         self.coffee_crud.delete(coffee_id)


coffee_service = CoffeeService(coffee_crud=coffee_crud_instance)
