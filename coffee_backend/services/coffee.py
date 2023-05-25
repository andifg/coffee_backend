from motor.motor_asyncio import AsyncIOMotorClientSession  # type: ignore

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

        Args:
            db_session (AsyncIOMotorClientSession): The database session object.
            coffee (Coffee): The coffee object to be added.

        Returns:
            Coffee: The added coffee object.

        Raises:
            Exception: If an error occurs while creating the coffee.
        """
        await self.coffee_crud.create(coffee=coffee, db_session=db_session)

        return coffee


#     def get_coffee(self, coffee_id):q
#         return self.coffee_crud.read(coffee_id)

#     def update_coffee(self, coffee_id, updated_coffee):
#         self.coffee_crud.update(coffee_id, updated_coffee)

#     def delete_coffee(self, coffee_id):
#         self.coffee_crud.delete(coffee_id)


coffee_service = CoffeeService(coffee_crud=coffee_crud_instance)
