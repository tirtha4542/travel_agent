import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agent.tools.tavily_tool import tavily_search
from app.agent.tools.flight_tool import resolve_airport_code, search_flights
from app.agent.graph import run_travel_agent

print("=== 1. Testing Natural Language Flight Search Query ===")
nl_query = "plan a 7 day napal treap from bangladesh"
print(f"Query: '{nl_query}'\n")
print(search_flights.invoke(nl_query))

print("\n=== 2. Testing Airport Resolution ===")
print("Dhaka  ->", resolve_airport_code("Dhaka"))      # DAC
print("Nepal  ->", resolve_airport_code("Nepal"))      # KTM
print("Japan  ->", resolve_airport_code("Japan"))      # HND
print("London ->", resolve_airport_code("London"))     # LHR

print("\n=== 3. Testing Direct Route (London to Paris) ===")
print(search_flights.invoke({"destination": "Paris", "origin": "London"}))

print("\n=== 4. Testing Tavily Web Search ===")
search_query = "top places to visit in Nepal Kathmandu Pokhara"
print(tavily_search(search_query))

print("\n" + "=" * 50)
print("=== 5. Testing Full Travel Agent (LangGraph Modular) ===")
print("=" * 50)
res = run_travel_agent("plan a 7 day napal treap from bangladesh")
print("\n[AGENT FINAL ANSWER]:\n")
print(res["answer"])
print("\n[METADATA]:")
print(f"Thread ID: {res['thread_id']}")
print(f"LLM Calls: {res['llm_calls']}")
