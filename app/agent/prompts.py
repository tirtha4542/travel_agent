ITINERARY_SYSTEM_PROMPT = "You are an expert travel planner."

def get_itinerary_prompt(user_query: str, flight_results: str, hotel_results: str) -> str:
    return f"""Create a complete travel itinerary.

User query: {user_query}

Flight results: {flight_results}

Hotel results: {hotel_results}

Make the itinerary practical, budget-aware, and easy to follow."""


FINAL_SYSTEM_PROMPT = "You are an expert travel consultant."

def get_final_prompt(user_query: str, flight_results: str, hotel_results: str, itinerary: str) -> str:
    return f"""Generate the final travel response for the user.

User request: {user_query}

Flight results:
{flight_results}

Hotel results:
{hotel_results}

Itinerary:
{itinerary}

Format the final answer beautifully using these sections:
1. Trip summary
2. Flight details
3. Hotel details
4. Itinerary
5. Budget summary
6. Final recommendation

Important:
- Be clear and professional
- Provide actionable insights
- Use markdown for formatting
- Highlight key information"""

