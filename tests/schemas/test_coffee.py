from coffee_backend.schemas.coffee import Coffee
from coffee_backend.schemas.rating import Rating


def test_coffee_creation_without_ratings() -> None:
    """Test coffee schema creation without any ratings."""
    coffee = Coffee(id="1", name="Homebrew", ratings=[])

    assert coffee.dict() == {"id": "1", "name": "Homebrew", "ratings": []}


def test_coffee_creation_with_ratings() -> None:
    """Test coffee schema creation with ratings."""
    rating_1 = Rating(id="1", rating=4)
    rating_2 = Rating(id="2", rating=3)

    coffee = Coffee(id="1", name="Nice", ratings=[rating_1, rating_2])

    assert coffee.dict() == {
        "id": "1",
        "name": "Nice",
        "ratings": [{"id": "1", "rating": 4}, {"id": "2", "rating": 3}],
    }
