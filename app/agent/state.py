import operator
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage


class TravelState(TypedDict):
    """LangGraph state schema for travel planning agent workflow."""
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int

