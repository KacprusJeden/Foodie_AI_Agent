import os
import json
from typing import List
from pydantic import TypeAdapter
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from foodie_ai_agent.models import Idea, Restaurant, RestaurantLink
from foodie_ai_agent.tools import tool_kit


SYSTEM_PROMPT = (
    "You are a foodie ReAct agent. Work step by step:\n"
    "1. Always call the build_idea tool first with the user's raw request.\n"
    "2. Call get_restaurants once for EACH phrase from the idea list. "
    "If the user asks only for links/pages, call get_restaurants_pages instead.\n"
    "3. From all the returned JSON, pick only the 3-5 best-matching restaurants.\n"
    "Return ONLY a raw JSON array (no markdown, no commentary). By default each "
    "object has exactly the Restaurant schema fields: name, address, opening_hours, "
    "price_range, food, rating, contact, link, location_pin (googleMapsUri goes to "
    "location_pin, websiteUri to link). If the user asks only for links/pages, each "
    "object has exactly the RestaurantLink schema fields: link, location_pin. "
    "Use null for missing data."
)


llm = init_chat_model(
    model="gpt-5.1",
    api_key=os.environ.get("OPENAI_API_KEY")
)


agent = create_agent(
    model=llm,
    tools=tool_kit,
    system_prompt=SYSTEM_PROMPT
)


def parse_answer(answer: str) -> List[Restaurant] | List[RestaurantLink]:
    answer = answer.strip()
    if answer.startswith("```"):
        answer = answer.split("\n", 1)[1].rsplit("```", 1)[0]

    raw = json.loads(answer)
    if raw and "name" not in raw[0]:
        return TypeAdapter(List[RestaurantLink]).validate_python(raw)

    for item in raw:
        if isinstance(item.get("opening_hours"), list):
            item["opening_hours"] = "; ".join(item["opening_hours"])
        if isinstance(item.get("food"), str):
            item["food"] = [f.strip() for f in item["food"].split(",")]
    return TypeAdapter(List[Restaurant]).validate_python(raw)


def format_restaurants(restaurants: List[Restaurant] | List[RestaurantLink]) -> str:
    lines = []
    for i, r in enumerate(restaurants, start=1):
        if isinstance(r, RestaurantLink):
            block = [f"{i}."]
            if r.link:
                block.append(f"   Website:  {r.link}")
            if r.location_pin:
                block.append(f"   Pin:      {r.location_pin}")
        else:
            block = [
                f"{i}. {r.name}  ({r.rating}/5)" if r.rating else f"{i}. {r.name}",
                f"   Address:  {r.address}",
            ]
            if r.opening_hours:
                block.append(f"   Hours:    {r.opening_hours}")
            if r.price_range:
                block.append(f"   Prices:   {r.price_range}")
            if r.food:
                block.append(f"   Food:     {', '.join(r.food)}")
            if r.contact:
                block.append(f"   Contact:  {r.contact}")
            if r.link:
                block.append(f"   Website:  {r.link}")
            if r.location_pin:
                block.append(f"   Pin:      {r.location_pin}")
        lines.append("\n".join(block))
    return "\n\n".join(lines)


if __name__ == "__main__":
    query = input("Enter the query: ")
    result = agent.invoke({"messages": [("user", query)]}, stream_mode="values")
    answer = result["messages"][-1].content

    restaurants = parse_answer(answer)
    print(format_restaurants(restaurants))
