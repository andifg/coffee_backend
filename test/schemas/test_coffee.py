from coffee_backend.schemas.coffee import Coffee



def test_coffee_creation_without_ratings():
    coffee = Coffee(id=1,name="Homebrew")

    assert coffee.dict() == {'id': '1', 'name': 'Homebrew', 'ratings': []}