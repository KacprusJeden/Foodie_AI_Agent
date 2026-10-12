"""Unit tests for agent helpers."""

from foodie_ai_agent.agent import format_restaurants, parse_answer
from foodie_ai_agent.models import Restaurant, RestaurantLink


def test_parse_answer_converts_markdown_wrapped_restaurants() -> None:
    """Validate parsing and normalization of restaurant payloads."""
    answer = """```json
    [
      {
        "name": "Bistro Test",
        "address": "ul. Przykladowa 1, Warszawa",
        "opening_hours": ["Mon-Fri 10:00-22:00", "Sat-Sun 11:00-23:00"],
        "price_range": "40-80 PLN",
        "food": "pizza, pasta",
        "rating": 4.7,
        "contact": "+48 111 222 333",
        "link": "https://bistro.test",
        "location_pin": "https://maps.google.com/test"
      }
    ]
    ```"""

    result = parse_answer(answer)

    assert len(result) == 1
    assert isinstance(result[0], Restaurant)
    assert result[0].opening_hours == "Mon-Fri 10:00-22:00; Sat-Sun 11:00-23:00"
    assert result[0].food == ["pizza", "pasta"]


def test_parse_answer_returns_restaurant_links_when_name_is_missing() -> None:
    """Validate parsing of the links-only response shape."""
    answer = (
        "[{\"link\": \"https://example.com\", "
        "\"location_pin\": \"https://maps.google.com/example\"}]"
    )

    result = parse_answer(answer)

    assert len(result) == 1
    assert isinstance(result[0], RestaurantLink)
    assert result[0].link == "https://example.com"


def test_format_restaurants_renders_full_restaurant_details() -> None:
    """Validate formatting for the Restaurant presentation."""
    restaurant = Restaurant(
        name="Bistro Test",
        address="ul. Przykladowa 1, Warszawa",
        opening_hours="Mon-Fri 10:00-22:00",
        price_range="40-80 PLN",
        food=["pizza", "pasta"],
        rating=4.7,
        contact="+48 111 222 333",
        link="https://bistro.test",
        location_pin="https://maps.google.com/test",
    )

    result = format_restaurants([restaurant])

    assert "1. Bistro Test  (4.7/5)" in result
    assert "Address:  ul. Przykladowa 1, Warszawa" in result
    assert "Food:     pizza, pasta" in result
    assert "Website:  https://bistro.test" in result


def test_format_restaurants_renders_links_only_variant() -> None:
    """Validate formatting for the RestaurantLink presentation."""
    restaurant_link = RestaurantLink(
        link="https://example.com",
        location_pin="https://maps.google.com/example",
    )

    result = format_restaurants([restaurant_link])

    assert "1." in result
    assert "Website:  https://example.com" in result
    assert "Pin:      https://maps.google.com/example" in result
