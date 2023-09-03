from typing import List
from uuid import UUID

from fastapi import HTTPException, Response
from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore

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
        self, db_session: AsyncIOMotorClientSession, rating: Rating
    ) -> Rating:
        """
        Adds a new rating to the database.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.
            rating (Rating): The rating object to be added.

        Returns:
            Coffee: The added rating object.

        Raises:
            Exception: If an error occurs while creating the coffee.
        """

        return await self.rating_crud.create(
            rating=rating, db_session=db_session
        )

    async def list(self, db_session: AsyncIOMotorClientSession) -> List[Rating]:
        """Retrieve a list of coffee objects from the database.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.

        Returns:
            List[Coffee]: A list of coffee objects retrieved from the crud
                class.

        """
        try:
            coffees = await self.rating_crud.read(
                db_session=db_session, query={}
            )
        except ObjectNotFoundError:
            return []
        return coffees

    async def list_ids_for_coffee(
        self, db_session: AsyncIOMotorClientSession, coffee_id: UUID
    ) -> List[UUID]:
        """Retrieve a list of all rating ids for a certain coffee.

        This method returns a list of all ratings for a certain coffee. This is
        done via the cofee_id field in the rating object.


        Args:
            db_session (AsyncIOMotorClientSession): The database session object.

        Returns:
            List[UUID]: A list of rating ids.

        """
        try:
            ratings = await self.rating_crud.read(
                db_session=db_session,
                query={"coffee_id": coffee_id},
                projection={},
            )
        except ObjectNotFoundError:
            return []
        return [rating.id for rating in ratings]

    async def get_by_id(
        self, db_session: AsyncIOMotorClientSession, rating_id: UUID
    ) -> Rating:
        """
        Retrieve a rating object by its ID from the database.

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.
            id (UUID): The ID of the rating to retrieve.

        Returns:
            Coffee: The rating object matching the ID.

        """
        try:
            coffees = await self.rating_crud.read(
                db_session=db_session, query={"_id": rating_id}
            )
        except ObjectNotFoundError as error:
            raise HTTPException(
                status_code=404, detail="No rating found for given id"
            ) from error
        return coffees[0]

    async def delete_rating(
        self,
        db_session: AsyncIOMotorClientSession,
        rating_id: UUID,
    ) -> None:
        """
        Delete a coffee by ID.

        Args:
            db_session (AsyncIOMotorClientSession): The database session.
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


coffee_service = RatingService(rating_crud=rating_crud_instance)
