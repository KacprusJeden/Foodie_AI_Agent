"""Unit tests for tools module."""

from __future__ import annotations

import importlib
from types import SimpleNamespace


def test_build_idea_returns_serialized_model_dump(monkeypatch) -> None:
    """Validate build_idea delegates to the structured LLM and dumps the model."""
    tools_module = importlib.import_module("foodie_ai_agent.tools")

    captured_messages: list[object] = []

    class FakeIdea:
        """Fake Pydantic-like object returned by the model."""

        def model_dump(self) -> dict[str, list[str]]:
            return {"idea": ["Restauracja na randke Warszawa"]}

    class FakeIdeaLlm:
        """Fake LLM object used to capture invocations."""

        def invoke(self, messages: list[object]) -> FakeIdea:
            captured_messages.extend(messages)
            return FakeIdea()

    monkeypatch.setattr(tools_module, "idea_llm", FakeIdeaLlm())

    result = tools_module.build_idea("Szukam miejsca na randke w Warszawie")

    assert result == {"idea": ["Restauracja na randke Warszawa"]}
    assert captured_messages[0][0] == "system"
    assert captured_messages[1] == ("human", "Szukam miejsca na randke w Warszawie")


def test_get_restaurants_calls_google_places_with_full_field_mask(monkeypatch) -> None:
    """Validate get_restaurants sends the expected request and field mask."""
    tools_module = importlib.import_module("foodie_ai_agent.tools")

    captured: dict[str, object] = {}
    fake_places = [SimpleNamespace(display_name="Test")]

    class FakePlacesClient:
        """Capture request parameters passed to Google Places."""

        def __init__(self, client_options: dict[str, object]) -> None:
            captured["client_options"] = client_options

        def search_text(self, request: object, metadata: list[tuple[str, str]]) -> object:
            captured["request"] = request
            captured["metadata"] = metadata
            return SimpleNamespace(places=fake_places)

    monkeypatch.setenv("Google Place API Key", "test-api-key")
    monkeypatch.setattr(tools_module.places_v1, "PlacesClient", FakePlacesClient)

    result = tools_module.get_restaurants("pizza warszawa")

    assert result == fake_places
    assert captured["client_options"] == {"api_key": "test-api-key"}
    assert captured["request"].text_query == "pizza warszawa"
    assert captured["metadata"] == [
        (
            "x-goog-fieldmask",
            "places.displayName,places.formattedAddress,"
            "places.regularOpeningHours,places.priceRange,places.rating,places.primaryTypeDisplayName,"
            "places.nationalPhoneNumber,places.websiteUri,places.googleMapsUri",
        )
    ]


def test_get_restaurants_pages_calls_google_places_with_links_only(monkeypatch) -> None:
    """Validate get_restaurants_pages requests only page-related fields."""
    tools_module = importlib.import_module("foodie_ai_agent.tools")

    captured: dict[str, object] = {}
    fake_places = [SimpleNamespace(websiteUri="https://example.com")]

    class FakePlacesClient:
        """Capture request parameters passed to Google Places."""

        def __init__(self, client_options: dict[str, object]) -> None:
            captured["client_options"] = client_options

        def search_text(self, request: object, metadata: list[tuple[str, str]]) -> object:
            captured["request"] = request
            captured["metadata"] = metadata
            return SimpleNamespace(places=fake_places)

    monkeypatch.setenv("Google Place API Key", "test-api-key")
    monkeypatch.setattr(tools_module.places_v1, "PlacesClient", FakePlacesClient)

    result = tools_module.get_restaurants_pages("kawiarnia warszawa")

    assert result == fake_places
    assert captured["client_options"] == {"api_key": "test-api-key"}
    assert captured["request"].text_query == "kawiarnia warszawa"
    assert captured["metadata"] == [
        ("x-goog-fieldmask", "places.websiteUri,places.googleMapsUri")
    ]
