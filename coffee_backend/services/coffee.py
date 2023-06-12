import logging
from typing import List
from uuid import UUID

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
        try:
            coffees = await self.coffee_crud.read(
                db_session=db_session, query={}
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No coffees found"
            ) from error
        return coffees

    async def list_ids(
        self, db_session: AsyncIOMotorClientSession
    ) -> List[UUID]:
        """Retrieve a list of all coffee ids.

        This method returns a list of all coffee ids in the coffee collection.
        It utilizes the coffee crud read method to return coffees that only
        contain the necessary fields id and name but not the ratings for
        performance reasons by using a mongodb projection. It then only returns
        the ids of the returned coffees.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.

        Returns:
            List[UUID]: A list of coffee ids

        Raises:
            HTTPException: If no coffee IDs are found in the collection.

        """
        try:
            coffees = await self.coffee_crud.read(
                db_session=db_session,
                query={},
                projection={"_id": 1, "name": 1},
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No ids found"
            ) from error
        return [coffee.id for coffee in coffees]

    async def get_by_id(
        self, db_session: AsyncIOMotorClientSession, coffee_id: UUID
    ) -> Coffee:
        """
        Retrieve a coffee object by its ID from the database.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.
            id (UUID): The ID of the coffee to retrieve.

        Returns:
            Coffee: The coffee object matching the ID.

        """
        try:
            coffees = await self.coffee_crud.read(
                db_session=db_session, query={"_id": coffee_id}
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No coffee found for given id"
            ) from error
        return coffees[0]


#     def update_coffee(self, coffee_id, updated_coffee):
#         self.coffee_crud.update(coffee_id, updated_coffee)

#     def delete_coffee(self, coffee_id):
#         self.coffee_crud.delete(coffee_id)


coffee_service = CoffeeService(coffee_crud=coffee_crud_instance)
