import logging
from uuid import UUID

from fastapi import HTTPException, Request


def authorize_coffee_edit_delete(
    request: Request, coffee_owner_id: UUID
) -> None:
    """Authorize the user to edit or delete a coffee.

    This method checks if the user is allowed to edit or delete a coffee.

    Args:
        request (Request): The request object
        coffee_id (str): The ID of the coffee to edit or delete

    Returns:
        None

    """
    token = request.state.token

    roles = token.get("realm_access", {}).get("roles", [])
    if "admin" in roles:
        return

    user_id = token.get("sub", None)

    if user_id == coffee_owner_id:
        return

    logging.debug(
        "User %s is not authorized to edit or delete coffee with id %s.",
        user_id,
        coffee_owner_id,
    )
    raise HTTPException(
        status_code=403,
        detail="You are not authorized to edit or delete this coffee.",
    )
