from coffee_backend.schemas.rating import Rating


def test_rating() -> None:
    rating = Rating(id="1", rating=4)

    assert rating.dict() == {"id": "1", "rating": 4}
