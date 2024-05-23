import logging
from typing import Any, List, Optional
from uuid import UUID

from fastapi import HTTPException
from motor.core import AgnosticClientSession

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.coffee import CoffeeCRUD
from coffee_backend.mongo.coffee import coffee_crud as coffee_crud_instance
from coffee_backend.schemas.coffee import Coffee, UpdateCoffee


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
        self, db_session: AgnosticClientSession, coffee: Coffee
    ) -> Coffee:
        """
        Adds a new coffee to the database.

        Check whether name is already existing. If not create new coffee object.

        Args:
            db_session (AgnosticClientSession): The database session object.
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

    async def list(self, db_session: AgnosticClientSession) -> List[Coffee]:
        """Retrieve a list of coffee objects from the database.

        Args:
            db_session (AgnosticClientSession): The database session object.

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

    async def list_coffees_with_rating_summary(
        self,
        db_session: AgnosticClientSession,
        owner_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10,
        first_id: Optional[UUID] = None,
    ) -> List[Coffee]:
        """Retrieve a list of coffee objects from the database with rating
            summary.

        Args:
            db_session (AgnosticClientSession): The database session object.


        Returns:
            List[Coffee]: A list of coffee objects retrieved from the crud
                class.

        """

        pipeline = self._create_pipeline(
            owner_id=owner_id, page=page, page_size=page_size, first_id=first_id
        )

        try:
            coffees = await self.coffee_crud.aggregate_read(
                db_session=db_session, pipeline=pipeline
            )

        except ObjectNotFoundError:
            return []

        return coffees

    async def list_ids(self, db_session: AgnosticClientSession) -> List[UUID]:
        """Retrieve a list of all coffee ids.

        This method returns a list of all coffee ids in the coffee collection.
        It utilizes the coffee crud read method to return coffees that only
        contain the necessary fields id and name but not the ratings for
        performance reasons by using a mongodb projection. It then only returns
        the ids of the returned coffees.

        Args:
            db_session (AgnosticClientSession): The database session object.

        Returns:
            List[UUID]: A list of coffee ids

        Raises:
            HTTPException: If no coffee IDs are found in the collection.

        """
        try:
            coffees = await self.coffee_crud.read(
                db_session=db_session,
                query={},
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No ids found"
            ) from error
        return [coffee.id for coffee in coffees]

    def _create_pipeline(
        self,
        owner_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10,
        first_id: Optional[UUID] = None,
    ) -> List[dict]:
        pipeline: List[dict[str, Any]] = [{"$sort": {"_id": -1}}]

        if owner_id:
            pipeline.append({"$match": {"owner_id": owner_id}})

        if first_id:
            pipeline.append({"$match": {"_id": {"$lte": first_id}}})

        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "rating",
                        "localField": "_id",
                        "foreignField": "coffee_id",
                        "as": "rating",
                    }
                },
                {
                    "$addFields": {
                        "rating_count": {"$size": "$rating"},
                        "rating_average": {
                            "$round": [{"$avg": "$rating.rating"}, 2]
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "owner_id": 1,
                        "owner_name": 1,
                        "rating_count": 1,
                        "rating_average": 1,
                    }
                },
                {"$limit": page_size * page},
                {"$skip": (page - 1) * page_size},
            ]
        )

        logging.debug("Executing pipeline: %s", pipeline)

        return pipeline

    async def get_by_id(
        self, db_session: AgnosticClientSession, coffee_id: UUID
    ) -> Coffee:
        """
        Retrieve a coffee object by its ID from the database.

        Args:
            db_session (AgnosticClientSession): The database session object.
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

    async def patch_coffee(
        self,
        db_session: AgnosticClientSession,
        coffee_id: UUID,
        update_coffee: UpdateCoffee,
    ) -> Coffee:
        """
        Manage patch of coffee in database.

        Args:
            db_session (AgnosticClientSession): The database session object.
            coffee_id (UUID): The ID of the coffee to update.
            update_coffee (UpdateCoffee): The updated coffee object.

        Returns:
            Coffee: The updated coffee object.

        Raises:
            HTTPException: If no coffee is found for the given ID.
        """

        coffee = await self.get_by_id(
            db_session=db_session, coffee_id=coffee_id
        )

        for attribute in update_coffee.dict():
            setattr(coffee, attribute, getattr(update_coffee, attribute))

        try:
            updated_coffee = await self.coffee_crud.update(
                db_session=db_session, coffee_id=coffee_id, coffee=coffee
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No coffee found for given id"
            ) from error
        return updated_coffee

    async def delete_coffee(
        self,
        db_session: AgnosticClientSession,
        coffee_id: UUID,
    ) -> None:
        """
        Delete a coffee by ID.

        Args:
            db_session (AgnosticClientSession): The database session.
            coffee_id (UUID): The ID of the coffee to delete.

        Raises:
            HTTPException: If the coffee with the given ID is not found in db.

        Returns:
            None
        """
        try:
            await self.coffee_crud.delete(
                db_session=db_session, coffee_id=coffee_id
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No coffee found for given id"
            ) from error


coffee_service = CoffeeService(coffee_crud=coffee_crud_instance)
