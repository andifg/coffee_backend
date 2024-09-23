import logging
from typing import Any, List, Optional
from uuid import UUID

from fastapi import HTTPException
from motor.core import AgnosticClientSession

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.drink import DrinkCRUD
from coffee_backend.mongo.drink import drink_crud as drink_crud_instance
from coffee_backend.schemas import Drink


class DrinkService:
    """Service layer between API and CRUD layer for handling drink-related
    operations.
    """

    def __init__(self, drink_crud: DrinkCRUD):
        """
        Initializes a new instance of the DrinkService class.

        Args:
            drink_crud (CoffeeCRUD): An instance of the DrinkCRUD class for
            performing CRUD operations.
        """
        self.drink_crud = drink_crud

    async def add_drink(
        self, db_session: AgnosticClientSession, drink: Drink
    ) -> Drink:
        """
        Adds a new drink to the database.

        Args:
            db_session (AgnosticClientSession): The database session object.
            drink (Drink): The drink object to be added.

        Returns:
            Coffee: The added drink object.

        Raises:
            Exception: If an error occurs while creating the coffee.
        """

        return await self.drink_crud.create(drink=drink, db_session=db_session)

    async def list(
        self,
        db_session: AgnosticClientSession,
        coffee_bean_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 5,
        first_drink_id: Optional[UUID] = None,
    ) -> List[Drink]:
        """Retrieve a list of coffee drinks from the database.

        Args:
            db_session (AgnosticClientSession): The database session object.

        Returns:
            List[Drink]: A list of drink objects retrieved from the crud
                class.

        """
        try:

            query: dict[str, Any] = {}

            if first_drink_id:
                query["_id"] = {"$lte": first_drink_id}

            if coffee_bean_id:
                query["coffee_bean_id"] = coffee_bean_id

            drinks = await self.drink_crud.read(
                db_session=db_session,
                query=query,
                limit=(page_size),
                skip=(page_size * (page - 1)),
            )
        except ObjectNotFoundError:
            return []
        return drinks

    async def list_drinks_with_coffee_bean_information(
        self,
        db_session: AgnosticClientSession,
        user_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10,
        first_id: Optional[UUID] = None,
        coffee_bean_id: Optional[UUID] = None,
    ) -> List[Drink]:
        """Retrieve a list of drinks objects from the database with coffee bean
        information.

        Args:
            db_session (AgnosticClientSession): The database session object.


        Returns:
            List[Coffee]: A list of coffee objects retrieved from the crud
                class.

        """

        pipeline = self._create_pipeline(
            user_id=user_id,
            page=page,
            page_size=page_size,
            first_id=first_id,
            coffee_bean_id=coffee_bean_id,
        )

        try:
            coffees = await self.drink_crud.aggregate_read(
                db_session=db_session, pipeline=pipeline
            )

        except ObjectNotFoundError:
            return []

        return coffees

    async def get_by_id(
        self, db_session: AgnosticClientSession, drink_id: UUID
    ) -> Drink:
        """
        Retrieve a drink object by its ID from the database.

        Args:
            db_session (AgnosticClientSession): The database session object.
            id (UUID): The ID of the drink to retrieve.

        Returns:
            Coffee: The drink object matching the ID.

        """
        try:
            coffees = await self.drink_crud.read(
                db_session=db_session,
                query={"_id": drink_id},
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No drink found for given id"
            ) from error
        return coffees[0]

    async def delete_drink(
        self,
        db_session: AgnosticClientSession,
        drink_id: UUID,
    ) -> None:
        """
        Delete a coffee by ID.

        Args:
            db_session (AgnosticClientSession): The database session.
            drink_id (UUID): The ID of the drink to delete.

        Raises:
            HTTPException: If the coffee with the given ID is not found in db.

        Returns:
            None
        """
        try:
            await self.drink_crud.delete(
                db_session=db_session, drink_id=drink_id
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No drink found for given id"
            ) from error

    async def delete_by_coffee_bean_id(
        self,
        db_session: AgnosticClientSession,
        coffee_bean_id: UUID,
    ) -> None:
        """
        Delete all drinks for a certain coffee.

        Args:
            db_session (AgnosticClientSession): The database session.
            coffee_bean_id (UUID): The ID of the coffee to delete drinks for.

        Raises:
            HTTPException: If the coffee with the given ID is not found in db.

        Returns:
            None
        """
        try:
            await self.drink_crud.delete_many(
                db_session=db_session, query={"coffee_bean_id": coffee_bean_id}
            )
        except ObjectNotFoundError:
            return None

    def _create_pipeline(
        self,
        user_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10,
        first_id: Optional[UUID] = None,
        coffee_bean_id: Optional[UUID] = None,
    ) -> List[dict]:
        """Create a pipeline to retrieve drinks with coffee bean information."""

        pipeline: List[dict[str, Any]] = [{"$sort": {"_id": -1}}]

        if user_id:
            pipeline.append({"$match": {"user_id": user_id}})

        if first_id:
            pipeline.append({"$match": {"_id": {"$lte": first_id}}})

        if coffee_bean_id:
            pipeline.append({"$match": {"coffee_bean_id": coffee_bean_id}})

        pipeline.extend(
            [
                {
                    "$lookup": {
                        "from": "coffee",
                        "localField": "coffee_bean_id",
                        "foreignField": "_id",
                        "as": "drink",
                    }
                },
                {
                    "$addFields": {
                        "coffee_bean_name": {
                            "$arrayElemAt": ["$drink.name", 0]
                        },
                        "coffee_bean_roasting_company": {
                            "$arrayElemAt": ["$drink.roasting_company", 0]
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "brewing_method": 1,
                        "rating": 1,
                        "coffee_bean_id": 1,
                        "user_id": 1,
                        "user_name": 1,
                        "image_exists": 1,
                        "coffee_bean_name": 1,
                        "coffee_bean_roasting_company": 1,
                    }
                },
                {"$limit": page_size * page},
                {"$skip": (page - 1) * page_size},
            ]
        )

        logging.debug("Executing pipeline: %s", pipeline)

        return pipeline


drink_service = DrinkService(drink_crud=drink_crud_instance)
