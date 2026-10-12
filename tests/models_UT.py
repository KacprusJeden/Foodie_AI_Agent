"""Unit tests for Pydantic models."""

from foodie_ai_agent.models import Idea, Restaurant, RestaurantLink


def test_idea_accepts_a_list_of_search_phrases() -> None:
    """Validate that Idea stores the phrase list unchanged."""
    idea = Idea(idea=["Kebab Warszawa Stare Miasto", "Tania pizza Mokotow"])

    assert idea.idea == ["Kebab Warszawa Stare Miasto", "Tania pizza Mokotow"]


def test_restaurant_uses_safe_defaults_for_optional_fields() -> None:
    """Validate Restaurant defaults for missing optional data."""
    restaurant = Restaurant(name="Miejsce", address="ul. Testowa 1, Warszawa")

    assert restaurant.opening_hours is None
    assert restaurant.price_range is None
    assert restaurant.food == []
    assert restaurant.rating is None
    assert restaurant.contact is None
    assert restaurant.link is None
    assert restaurant.location_pin is None


def test_restaurant_link_allows_missing_values() -> None:
    """Validate RestaurantLink optional fields."""
    restaurant_link = RestaurantLink()

    assert restaurant_link.link is None
    assert restaurant_link.location_pin is None
