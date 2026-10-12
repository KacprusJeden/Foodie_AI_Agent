import os
from typing import List
from google.maps import places_v1
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from foodie_ai_agent.models import Idea


IDEA_SYSTEM_PROMPT = (
    "You are a restaurant-search assistant. Always call the build_idea tool first. "
    "For now, your only job is to transform the user's request into the Idea schema. "
    "Do not search Google Places yet. After using the tool, return the final answer "
    "as structured data matching the Idea schema."
)


idea_llm = init_chat_model(
    model="gpt-5.1",
    api_key=os.environ.get("OPENAI_API_KEY")
).with_structured_output(Idea)


@tool
def build_idea(user_query: str) -> dict:
    """Convert the user's long restaurant request into a short Google Places query."""
    idea = idea_llm.invoke(
        [
            ("system", IDEA_SYSTEM_PROMPT),
            ("human", user_query),
        ]
    )
    return idea.model_dump()


@tool
def get_restaurants(query: str) -> List:
    """Search Google Places using a short query phrase prepared for places lookup."""
    client = places_v1.PlacesClient(
        client_options={"api_key": os.environ["Google Place API Key"]}
    )

    request = places_v1.SearchTextRequest(
        text_query=query
    )

    response = client.search_text(
        request=request,
        metadata=[
            (
                "x-goog-fieldmask",
                "places.displayName,places.formattedAddress,"
                "places.regularOpeningHours,places.priceRange,places.rating,places.primaryTypeDisplayName,"
                "places.nationalPhoneNumber,places.websiteUri,places.googleMapsUri"
            ),
        ],
    )

    return response.places


@tool
def get_restaurants_pages(query: str) -> List:
    """Search Google Places using a short query phrase prepared for places lookup.\
    Return only website and Google Maps Pin Location"""

    client = places_v1.PlacesClient(
        client_options={"api_key": os.environ["Google Place API Key"]}
    )

    request = places_v1.SearchTextRequest(
        text_query=query
    )

    response = client.search_text(
        request=request,
        metadata=[
            (
                "x-goog-fieldmask",
                "places.websiteUri,places.googleMapsUri"
            ),
        ],
    )

    return response.places


tool_kit = [build_idea, get_restaurants, get_restaurants_pages]