from uuid import UUID

import pytest
from pydantic import ValidationError

from coffee_backend.schemas.rating_summary import RatingSummary


def test_create_rating_summary_schema_creation() -> None:
    """Test creation of Rating Summary schema."""
    rating_summary = RatingSummary(
        coffee_id=UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        rating_count=4,
        rating_average=4.5,
    )

    assert rating_summary.model_dump(by_alias=True) == {
        "coffee_id": UUID("c9ba633e-c37c-11ed-afb4-acde48001122"),
        "rating_count": 4,
        "rating_average": 4.5,
    }


def test_create_rating_summary_with_invalid_id() -> None:
    """Test creating a Rating Summary instance with an invalid id."""
    with pytest.raises(ValidationError):
        RatingSummary(
            coffee_id="invalid_id",  # type: ignore
            rating_count=6,
            rating_average=8.0,
        )


def test_create_rating_summary_without_id() -> None:
    """Test creating a Rating instance with an invalid id."""
    with pytest.raises(ValidationError):
        RatingSummary(rating_average=3.0)  # type: ignore
