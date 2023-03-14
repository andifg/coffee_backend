from coffee_backend.schemas.rating import Rating


def test_rating_schema_creation() -> None:
    """Test creation of rating schema."""
    rating = Rating(id="1", rating=4)

    assert rating.dict() == {"id": "1", "rating": 4}
