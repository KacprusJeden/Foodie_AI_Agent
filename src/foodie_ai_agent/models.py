from typing import List
from pydantic import BaseModel, Field


class Idea(BaseModel):
    idea: List[str] = Field(
        description=(
            "Short Google Places search phrase or a short list of phrases derived "
            "from the user's longer request. Keep only the core venue type, cuisine, "
            "location, and essential constraints."
        )
    )


class Restaurant(BaseModel):
    name: str = Field(description="Name of the restaurant")

    address: str = Field(
        description="Full address of the restaurant"
    )

    opening_hours: str | None = Field(
        default=None,
        description="Opening hours, if available"
    )

    price_range: str | None = Field(
        default=None,
        description="Approximate meal price in PLN, if available"
    )

    food: list[str] = Field(
        default_factory=list,
        description="Examples of dishes or food types, if available"
    )

    rating: float | None = Field(
        default=None,
        description="Google rating, if available"
    )

    contact: str | None = Field(
        default=None,
        description="Phone number, if available"
    )

    link: str | None = Field(
        default=None,
        description="Website if available"
    )

    location_pin: str | None = Field(
        default=None,
        description="Google Maps link if available"
    )


class RestaurantLink(BaseModel):
    link: str | None = Field(
            default=None,
            description="Website if available"
        )
    
    location_pin: str | None = Field(
        default=None,
        description="Google Maps link if available"
    )