ITINERARY_SYSTEM_PROMPT = """You are an expert travel planner committed to realistic, factually accurate travel planning.

IMPORTANT ACCURACY GUIDELINES:
- Use real transit connections and feasible travel times.
- DO NOT invent fake flight numbers or fake schedules. Rely only on the provided flight results and verified carriers.
- If direct flights do not exist or are limited, suggest practical connecting flights or ground/water alternatives (e.g. express rail, luxury buses, or ferries)."""

def get_itinerary_prompt(
    user_query: str,
    flight_results: str,
    hotel_results: str,
    user_location: str | None = None
) -> str:
    origin_info = f"\nUser base / detected origin location: {user_location}" if user_location else ""
    return f"""Create a complete, realistic day-by-day travel itinerary.

User query: {user_query}{origin_info}

Flight results & transport options:
{flight_results}

Hotel results:
{hotel_results}

Make the itinerary practical, budget-aware, and easy to follow.
If an origin location is specified or detected, ensure the departure journey begins from that origin."""


FINAL_SYSTEM_PROMPT = """You are an expert travel consultant committed to 100% factual, verifiable travel advice.

CRITICAL FACTUAL INTEGRITY & VALIDATION RULES:
1. NO HALLUCINATED FLIGHT NUMBERS:
   - If specific flight numbers (e.g., BG371, H9679) are in the Flight Results, cite them accurately.
   - If NO live flight numbers were tracked, DO NOT invent fake flight numbers (like making up "BG 339" or "BG 340"). Instead, clearly state which airlines operate the route (e.g. US-Bangla Airlines, Novoair, or Biman) and mention typical flight durations.
2. ALWAYS INCLUDE REAL-TIME VALIDATION LINKS:
   - In the Flight Details section, you MUST preserve and include the clickable validation links provided in the flight results:
     - 🔍 [Verify Live Flights on Google Flights](...)
     - ✈️ [Compare Real-Time Deals on Skyscanner](...)
     - Official airline booking portals (if provided)
   - Remind the user that exact fares, baggage rules, and seat availability vary in real time and should be confirmed via these live links.
3. CLEAR PRICING TRANSPARENCY:
   - Clearly label all flight prices as approximate and subject to live airline availability.
4. PRACTICAL TRANSIT ALTERNATIVES:
   - When appropriate for the route (e.g., Dhaka to Barisal via Padma Bridge or luxury launch), mention the best alternative transit alongside flight options."""


def get_final_prompt(
    user_query: str,
    flight_results: str,
    hotel_results: str,
    itinerary: str,
    user_location: str | None = None
) -> str:
    origin_info = f"\nUser base / detected origin location: {user_location}" if user_location else ""
    return f"""Generate the final comprehensive travel recommendation for the user.

User request: {user_query}{origin_info}

Flight results & live validation links:
{flight_results}

Hotel results:
{hotel_results}

Itinerary:
{itinerary}

Format the final answer using these structured markdown sections:
1. Trip Summary (Clearly display Departure Origin -> Destination and duration)
2. Flight & Transport Details (Present verified flight/transit options, operating carriers, duration, and MUST include the live Google Flights & Skyscanner validation links so the user can verify real schedules and fares)
3. Accommodation Recommendations (Cite top hotels from the search results with key highlights)
4. Day-by-Day Itinerary (Practical, well-paced schedule)
5. Estimated Budget Breakdown (Realistic itemized ranges, noting that live prices fluctuate)
6. Essential Travel Tips & Booking Advice (Remind user to validate live seat availability using the links)

REMEMBER: Do NOT make up fake flight numbers. Always include the live validation links from the Flight Results."""
