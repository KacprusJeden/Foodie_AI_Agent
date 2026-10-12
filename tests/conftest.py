"""Pytest configuration and lightweight stubs for external SDKs."""

from __future__ import annotations

import sys
import types
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _install_langchain_stubs() -> None:
    """Install minimal LangChain stubs required by the unit tests."""
    langchain_module = types.ModuleType("langchain")
    chat_models_module = types.ModuleType("langchain.chat_models")
    tools_module = types.ModuleType("langchain.tools")
    agents_module = types.ModuleType("langchain.agents")

    class DummyChatModel:
        """Simple stand-in for a chat model used in imports."""

        def with_structured_output(self, _schema: object) -> "DummyChatModel":
            return self

        def invoke(self, _messages: object) -> object:
            return None

    class DummyAgent:
        """Simple stand-in for an agent used in imports."""

        def invoke(self, *_args: object, **_kwargs: object) -> dict[str, list[object]]:
            return {"messages": []}

    def init_chat_model(**_kwargs: object) -> DummyChatModel:
        return DummyChatModel()

    def tool(function: object) -> object:
        return function

    def create_agent(**_kwargs: object) -> DummyAgent:
        return DummyAgent()

    chat_models_module.init_chat_model = init_chat_model
    tools_module.tool = tool
    agents_module.create_agent = create_agent

    langchain_module.chat_models = chat_models_module
    langchain_module.tools = tools_module
    langchain_module.agents = agents_module

    sys.modules["langchain"] = langchain_module
    sys.modules["langchain.chat_models"] = chat_models_module
    sys.modules["langchain.tools"] = tools_module
    sys.modules["langchain.agents"] = agents_module


def _install_google_places_stubs() -> None:
    """Install minimal Google Places stubs required by the unit tests."""
    google_module = types.ModuleType("google")
    maps_module = types.ModuleType("google.maps")
    places_v1_module = types.ModuleType("google.maps.places_v1")

    class SearchTextRequest:
        """Simple request DTO used by the tool tests."""

        def __init__(self, text_query: str) -> None:
            self.text_query = text_query

    class PlacesClient:
        """Simple client stub used by the tool tests."""

        def __init__(self, client_options: dict[str, object] | None = None) -> None:
            self.client_options = client_options or {}

        def search_text(self, request: object, metadata: list[tuple[str, str]] | None = None) -> object:
            return types.SimpleNamespace(places=[], request=request, metadata=metadata)

    places_v1_module.SearchTextRequest = SearchTextRequest
    places_v1_module.PlacesClient = PlacesClient
    maps_module.places_v1 = places_v1_module
    google_module.maps = maps_module

    sys.modules["google"] = google_module
    sys.modules["google.maps"] = maps_module
    sys.modules["google.maps.places_v1"] = places_v1_module


_install_langchain_stubs()
_install_google_places_stubs()
