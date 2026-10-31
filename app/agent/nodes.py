import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agent.state import TravelState
from app.agent.prompts import (
    ITINERARY_SYSTEM_PROMPT,
    get_itinerary_prompt,
    FINAL_SYSTEM_PROMPT,
    get_final_prompt,
)
from app.agent.tools.flight_tool import search_flights
from app.agent.tools.tavily_tool import tavily_search

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY, max_tokens=1000)


def flight_agent(state: TravelState):
    """Fetches real-time flight options, honoring explicit query origin or user's detected location."""
    query = state["user_query"]
    user_location = state.get("user_location")

    # Pass user_location as fallback origin while letting query-specified origin take priority
    flight_data = search_flights.invoke({
        "query": query,
        "origin": user_location
    })

    # If no live radar flights were directly tracked, enrich with real-world web search insights
    if "Radar Tracker Status" in flight_data or "No active" in flight_data or "No live" in flight_data:
        try:
            web_insights = tavily_search(f"flights from {user_location or ''} for {query} airlines schedule booking price")
            if web_insights and "temporarily unavailable" not in web_insights:
                flight_data += f"\n\n### Web-Verified Route & Carrier Insights:\n{web_insights}"
        except Exception:
            pass

    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="flight results fetched")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def hotel_agent(state: TravelState):
    """Searches top-rated hotels using Tavily web search."""
    query = f"Best hotels for {state['user_query']}"
    hotel_data = tavily_search(query)
    return {
        "hotel_results": hotel_data,
        "messages": [AIMessage(content="hotel results fetched")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def itinerary_agent(state: TravelState):
    """Generates a day-by-day practical travel itinerary."""
    prompt = get_itinerary_prompt(
        user_query=state["user_query"],
        flight_results=state["flight_results"],
        hotel_results=state["hotel_results"],
        user_location=state.get("user_location")
    )

    response = llm.invoke([
        SystemMessage(content=ITINERARY_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def final_agent(state: TravelState):
    """Synthesizes all details into a formatted travel recommendation."""
    final_prompt = get_final_prompt(
        user_query=state["user_query"],
        flight_results=state["flight_results"],
        hotel_results=state["hotel_results"],
        itinerary=state["itinerary"],
        user_location=state.get("user_location")
    )

    response = llm.invoke([
        SystemMessage(content=FINAL_SYSTEM_PROMPT),
        HumanMessage(content=final_prompt),
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
