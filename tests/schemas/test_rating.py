from uuid import UUID

from coffee_backend.schemas.rating import Rating


def test_rating_schema_creation() -> None:
    """Test creation of rating schema."""
    rating = Rating(_id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"), rating=4)

    assert rating.dict(by_alias=True) == {
        "_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating": 4,
    }
