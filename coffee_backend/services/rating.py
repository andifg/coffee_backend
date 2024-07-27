from typing import Any, List, Optional
from uuid import UUID

from fastapi import HTTPException
from motor.core import AgnosticClientSession

from coffee_backend.exceptions.exceptions import ObjectNotFoundError
from coffee_backend.mongo.rating import RatingCRUD
from coffee_backend.mongo.rating import rating_crud as rating_crud_instance
from coffee_backend.schemas.rating import Rating


class RatingService:
    """Service layer between API and CRUD layer for handling rating-related
    operations.
    """

    def __init__(self, rating_crud: RatingCRUD):
        """
        Initializes a new instance of the RatingService class.

        Args:
            rating_crud (CoffeeCRUD): An instance of the RatingCRUD class for
            performing CRUD operations.
        """
        self.rating_crud = rating_crud

    async def add_rating(
        self, db_session: AgnosticClientSession, rating: Rating
    ) -> Rating:
        """
        Adds a new rating to the database.

        Args:
            db_session (AgnosticClientSession): The database session object.
            rating (Rating): The rating object to be added.

        Returns:
            Coffee: The added rating object.

        Raises:
            Exception: If an error occurs while creating the coffee.
        """

        return await self.rating_crud.create(
            rating=rating, db_session=db_session
        )

    async def list(
        self,
        db_session: AgnosticClientSession,
        coffee_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 5,
        first_rating_id: Optional[UUID] = None,
    ) -> List[Rating]:
        """Retrieve a list of coffee ratings from the database.

        Args:
            db_session (AgnosticClientSession): The database session object.

        Returns:
            List[Rating]: A list of rating objects retrieved from the crud
                class.

        """
        try:

            query: dict[str, Any] = {}

            if first_rating_id:
                query["_id"] = {"$lte": first_rating_id}

            if coffee_id:
                query["coffee_id"] = coffee_id

            ratings = await self.rating_crud.read(
                db_session=db_session,
                query=query,
                limit=(page_size),
                skip=(page_size * (page - 1)),
            )
        except ObjectNotFoundError:
            return []
        return ratings

    async def get_by_id(
        self, db_session: AgnosticClientSession, rating_id: UUID
    ) -> Rating:
        """
        Retrieve a rating object by its ID from the database.

        Args:
            db_session (AgnosticClientSession): The database session object.
            id (UUID): The ID of the rating to retrieve.

        Returns:
            Coffee: The rating object matching the ID.

        """
        try:
            coffees = await self.rating_crud.read(
                db_session=db_session,
                query={"_id": rating_id},
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No rating found for given id"
            ) from error
        return coffees[0]

    async def delete_rating(
        self,
        db_session: AgnosticClientSession,
        rating_id: UUID,
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
            await self.rating_crud.delete(
                db_session=db_session, rating_id=rating_id
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No rating found for given id"
            ) from error

    async def delete_by_coffee_id(
        self,
        db_session: AgnosticClientSession,
        coffee_id: UUID,
    ) -> None:
        """
        Delete all ratings for a certain coffee.

        Args:
            db_session (AgnosticClientSession): The database session.
            coffee_id (UUID): The ID of the coffee to delete.

        Raises:
            HTTPException: If the coffee with the given ID is not found in db.

        Returns:
            None
        """
        try:
            await self.rating_crud.delete_many(
                db_session=db_session, query={"coffee_id": coffee_id}
            )
        except ObjectNotFoundError:
            return None


rating_service = RatingService(rating_crud=rating_crud_instance)
