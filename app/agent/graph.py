# LangGraph workflow definition and compilation
import sys
from pathlib import Path
import uuid
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

# Ensure project root is in sys.path when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.agent.state import TravelState
from app.agent.nodes import flight_agent, hotel_agent, itinerary_agent, final_agent
from app.core.database import get_postgres_checkpointer

# 1. Initialize StateGraph
graph = StateGraph(TravelState)

# 2. Add Nodes
graph.add_node("flight", flight_agent)
graph.add_node("hotel", hotel_agent)
graph.add_node("itinerary", itinerary_agent)
graph.add_node("final", final_agent)

# 3. Add Edges
graph.add_edge(START, "flight")
graph.add_edge("flight", "hotel")
graph.add_edge("hotel", "itinerary")
graph.add_edge("itinerary", "final")
graph.add_edge("final", END)

# 4. Attach PostgreSQL checkpointer and compile
checkpointer = get_postgres_checkpointer()
travel_graph = graph.compile(checkpointer=checkpointer)
travel_grpah = travel_graph  # Backward-compatible alias for existing code


def run_travel_agent(
    user_query: str,
    thread_id: str | None = None,
    user_location: str | None = None
) -> dict:
    """Invokes the compiled multi-agent travel graph with memory persistence and location awareness."""
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = travel_graph.invoke({
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "user_location": user_location,
        "flight_results": "",
        "hotel_results": "",
        "itinerary": "",
        "llm_calls": 0,
    }, config=config)

    final_answer = result["messages"][-1].content
    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "user_location": user_location,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }


if __name__ == "__main__":
    test_res = run_travel_agent("i have to go london", user_location="Bangladesh")
    print(test_res["answer"])

if __name__ == "__main__":
    test_res = run_travel_agent("i have to go london", user_location="Bangladesh")
    print(test_res["answer"])

