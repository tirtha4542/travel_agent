import os
import re
import certifi
import airportsdata
import pycountry
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# SSL certificate configuration
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATION_STACK_API_KEY")
DEFAULT_ORIGIN = os.getenv("DEFAULT_ORIGIN", "DAC")
BASE_URL = "http://api.aviationstack.com/v1/flights"

# Load airport dataset by IATA codes
AIRPORTS = airportsdata.load("IATA")

COUNTRY_ALIASES = {
    # Nepal
    "nepal": "NP",
    "napal": "NP",
    "np": "NP",
    
    # Bangladesh
    "bangladesh": "BD",
    "bd": "BD",
    
    # India
    "india": "IN",
    "in": "IN",
    
    # Pakistan
    "pakistan": "PK",
    "pk": "PK",
    
    # Maldives
    "maldives": "MV",
    "maldive": "MV",
    "mv": "MV",
    
    # Sri Lanka
    "sri lanka": "LK",
    "srilanka": "LK",
    "lk": "LK",
    
    # Bhutan
    "bhutan": "BT",
    "bt": "BT",
    
    # Thailand
    "thailand": "TH",
    "thai": "TH",
    "th": "TH",
    
    # Malaysia
    "malaysia": "MY",
    "my": "MY",
    
    # Singapore
    "singapore": "SG",
    "sg": "SG",
    
    # Indonesia
    "indonesia": "ID",
    "id": "ID",
    
    # United Arab Emirates
    "uae": "AE",
    "u.a.e": "AE",
    "united arab emirates": "AE",
    "ae": "AE",
    
    # Saudi Arabia
    "saudi arabia": "SA",
    "saudi": "SA",
    "ksa": "SA",
    "sa": "SA",
    
    # Qatar
    "qatar": "QA",
    "qa": "QA",
    
    # Turkey
    "turkey": "TR",
    "turkiye": "TR",
    "tr": "TR",
    
    # United States
    "usa": "US",
    "u.s.a": "US",
    "u.s.a.": "US",
    "united states": "US",
    "united states of america": "US",
    "us": "US",
    
    # United Kingdom
    "uk": "GB",
    "u.k": "GB",
    "u.k.": "GB",
    "united kingdom": "GB",
    "great britain": "GB",
    "britain": "GB",
    "gb": "GB",
    
    # Canada
    "canada": "CA",
    "ca": "CA",
    
    # Australia
    "australia": "AU",
    "aussie": "AU",
    "au": "AU",
    
    # Germany
    "germany": "DE",
    "deutschland": "DE",
    "de": "DE",
    
    # France
    "france": "FR",
    "fr": "FR",
    
    # Japan
    "japan": "JP",
    "nippon": "JP",
    "jp": "JP",
    
    # China
    "china": "CN",
    "prc": "CN",
    "cn": "CN"
}

COUNTRY_MAIN_AIRPORT = {
    "NP": "KTM",  # Nepal (Kathmandu - Tribhuvan)
    "BD": "DAC",  # Bangladesh (Dhaka - Hazrat Shahjalal)
    "IN": "DEL",  # India (New Delhi - Indira Gandhi)
    "PK": "KHI",  # Pakistan (Karachi Jinnah)
    "MV": "MLE",  # Maldives (Male - Velana)
    "LK": "CMB",  # Sri Lanka (Colombo - Bandaranaike)
    "BT": "PBH",  # Bhutan (Paro)
    "TH": "BKK",  # Thailand (Bangkok - Suvarnabhumi)
    "MY": "KUL",  # Malaysia (Kuala Lumpur)
    "SG": "SIN",  # Singapore (Changi)
    "ID": "DPS",  # Indonesia (Bali - Ngurah Rai)
    "AE": "DXB",  # United Arab Emirates (Dubai)
    "SA": "RUH",  # Saudi Arabia (Riyadh - King Khalid)
    "QA": "DOH",  # Qatar (Doha - Hamad)
    "TR": "IST",  # Turkey (Istanbul)
    "US": "JFK",  # United States (New York - JFK)
    "GB": "LHR",  # United Kingdom (London - Heathrow)
    "CA": "YYZ",  # Canada (Toronto - Pearson)
    "AU": "SYD",  # Australia (Sydney - Kingsford Smith)
    "DE": "FRA",  # Germany (Frankfurt)
    "FR": "CDG",  # France (Paris - Charles de Gaulle)
    "JP": "HND",  # Japan (Tokyo - Haneda)
    "CN": "PEK"   # China (Beijing - Capital)
}

CITY_MAIN_AIRPORT = {
    # Nepal
    "kathmandu": "KTM",
    "pokhara": "PKR",
    
    # Bangladesh
    "dhaka": "DAC",
    "chittagong": "CGP",
    "sylhet": "ZYL",
    "coxs bazar": "CXB",
    "cox's bazar": "CXB",
    
    # Maldives & Sri Lanka
    "male": "MLE",
    "colombo": "CMB",
    
    # Southeast Asia
    "bangkok": "BKK",
    "phuket": "HKT",
    "kuala lumpur": "KUL",
    "singapore": "SIN",
    "bali": "DPS",
    "jakarta": "CGK",
    
    # Middle East
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "doha": "DOH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "medina": "MED",
    "istanbul": "IST",
    
    # India & Pakistan
    "delhi": "DEL",
    "mumbai": "BOM",
    "kolkata": "CCU",
    "chennai": "MAA",
    "bangalore": "BLR",
    "karachi": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",
    
    # United States
    "new york": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "san francisco": "SFO",
    "miami": "MIA",
    
    # United Kingdom & Europe
    "london": "LHR",
    "manchester": "MAN",
    "paris": "CDG",
    "frankfurt": "FRA",
    "berlin": "BER",
    "munich": "MUC",
    "rome": "FCO",
    "milan": "MXP",
    "madrid": "MAD",
    "barcelona": "BCN",
    "zurich": "ZRH",
    "geneva": "GVA",
    
    # Canada & Australia
    "toronto": "YYZ",
    "vancouver": "YVR",
    "sydney": "SYD",
    "melbourne": "MEL",
    
    # East Asia
    "tokyo": "HND",
    "osaka": "KIX",
    "beijing": "PEK",
    "shanghai": "PVG",
    "seoul": "ICN",
    "hong kong": "HKG"
}

STOP_WORDS = {
    'flight', 'flights', 'ticket', 'tickets', 'trip', 'trips', 'treap', 'treaps',
    'travel', 'travels', 'plan', 'plans', 'complete', 'days', 'day', 'including',
    'hotel', 'hotels', 'sightseeing', 'under', 'budget', 'info', 'information',
    'to', 'from', 'a', 'an', 'the', 'want', 'need', 'visit', 'go', 'for', 'in',
    'around', 'with', 'tour', 'tours', 'booking', 'book'
}


FILLER_WORDS = {
    'go', 'visit', 'travel', 'fly', 'trip', 'for trip', 'flights', 'flight',
    'tour', 'ticket', 'vacation', 'holiday', 'the', 'a', 'an'
}


def clean_text(text: str) -> str:
    """Normalizes text, fixes common typos, and strips conversational stop words."""
    if not text:
        return ""
    text = text.lower().strip()
    # Normalize common user typos
    text = re.sub(r"\btreap\b", "trip", text)
    text = re.sub(r"\bnapal\b", "nepal", text)
    text = re.sub(r"\btriep\b", "trip", text)
    text = re.sub(r"\bhavet\b", "have", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    words = [w for w in text.split() if w not in STOP_WORDS and not w.isdigit()]
    return " ".join(words).strip()


def extract_locations_from_query(query: str) -> tuple[str | None, str | None, str | None]:
    """Parses natural language travel queries into (origin, destination, date).
    
    Handles queries like:
    - 'i havet to go india to london give me the plan' -> ('india', 'london', None)
    - 'i have to go london' -> (None, 'london', None)
    - 'plan a 7 day napal treap from bangladesh' -> ('bangladesh', 'nepal trip', None)
    - 'flights from dhaka to nepal' -> ('dhaka', 'nepal', None)
    """
    q = query.strip()
    
    # Optional date extraction (YYYY-MM-DD)
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", q)
    flight_date = date_match.group(1) if date_match else None
    if flight_date:
        q = q.replace(flight_date, " ").strip()

    # Normalize common user typos
    q_norm = re.sub(r"\btreap\b", "trip", q, flags=re.IGNORECASE)
    q_norm = re.sub(r"\bnapal\b", "nepal", q_norm, flags=re.IGNORECASE)
    q_norm = re.sub(r"\bhavet\b", "have", q_norm, flags=re.IGNORECASE)

    # Strip conversational prefixes/suffixes
    cleaned = re.sub(r"\b(give me (the|a)?\s*(plan|itinerary)?|please|can you)\b", " ", q_norm, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(?:i\s+)?(?:have\s+to|want\s+to|need\s+to|would\s+like\s+to|plan\s+to|planning\s+to)\s+(?:go\s+to|travel\s+to|fly\s+to|visit|go|travel|fly)\s+", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(?:plan|make|create)\s+(?:a|the)?\s*(?:\d+\s*day[s]?)?\s*(?:trip|tour|itinerary)?\s*(?:to|for)?\s*", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Pattern 1: from <origin> to <destination>
    m1 = re.search(r"\bfrom\s+(.+?)\s+to\s+(.+)", cleaned, re.IGNORECASE)
    if m1:
        return m1.group(1).strip(), m1.group(2).strip(), flight_date

    # Pattern 2: to <destination> from <origin>
    m2 = re.search(r"\bto\s+(.+?)\s+from\s+(.+)", cleaned, re.IGNORECASE)
    if m2:
        return m2.group(2).strip(), m2.group(1).strip(), flight_date

    # Pattern 3: <destination phrase> from <origin>
    m3 = re.search(r"^(.*?)\s+from\s+(.+)", cleaned, re.IGNORECASE)
    if m3:
        return m3.group(2).strip(), m3.group(1).strip(), flight_date

    # Pattern 4: <origin> to <destination> (e.g. 'india to london', 'dhaka to tokyo')
    m4 = re.search(r"^([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+)$", cleaned, re.IGNORECASE)
    if m4:
        cand_orig = m4.group(1).strip()
        cand_dest = m4.group(2).strip()
        if cand_orig.lower() not in FILLER_WORDS:
            return cand_orig, cand_dest, flight_date
        else:
            return None, cand_dest, flight_date

    # Pattern 5: to <destination> or visit <destination>
    m5 = re.search(r"^(?:to|visit)\s+(.+)", cleaned, re.IGNORECASE)
    if m5:
        return None, m5.group(1).strip(), flight_date

    # Default fallback: entire query is treated as destination
    return None, cleaned, flight_date


def country_name_to_code(text: str) -> str | None:
    """Maps country names or aliases to a 2-letter ISO country code."""
    cleaned = clean_text(text)
    if cleaned in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[cleaned]
    try:
        country = pycountry.countries.lookup(cleaned)
        return country.alpha_2
    except LookupError:
        pass
    for country in pycountry.countries:
        country_name = country.name.lower()
        if country_name in cleaned or cleaned in country_name:
            return country.alpha_2
    for alias, code in COUNTRY_ALIASES.items():
        if alias in cleaned:
            return code
    return None


def airport_country_matches(airport: dict, country_code: str) -> bool:
    """Checks whether an airport dictionary matches the given 2-letter country code."""
    airport_country = str(airport.get('country', '')).upper().strip()
    if airport_country == country_code:
        return True
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except Exception:
        pass
    return False


def get_best_airport_for_country(country_code: str) -> str | None:
    """Finds the most prominent international airport for a given country code."""
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)
    if preferred and preferred in AIRPORTS:
        return preferred
    candidates = []
    for iata, airport in AIRPORTS.items():
        if not iata:
            continue
        if airport_country_matches(airport, country_code):
            name = str(airport.get('name', '')).lower()
            city = str(airport.get('city', '')).lower()
            score = 0
            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5
            candidates.append((score, iata))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def resolve_airport_code(query: str) -> str | None:
    """Resolves arbitrary user input (IATA, city, country, or natural phrase) to a 3-letter IATA code."""
    if not query:
        return None
    raw = query.strip().upper()
    # 1. Direct IATA code match
    if len(raw) == 3 and raw in AIRPORTS:
        return raw

    cleaned = clean_text(query)

    # 2. Check predefined city list
    if cleaned in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[cleaned]

    # Substring check for cities
    for city, iata in CITY_MAIN_AIRPORT.items():
        if city in cleaned:
            return iata

    # 3. Check country alias / pycountry lookup
    country_code = country_name_to_code(cleaned)
    if country_code:
        best_airport = get_best_airport_for_country(country_code)
        if best_airport:
            return best_airport

    # 4. Search AIRPORTS database by city or airport name
    for iata, airport in AIRPORTS.items():
        if not iata:
            continue
        airport_city = str(airport.get("city", "")).lower()
        airport_name = str(airport.get("name", "")).lower()
        if cleaned and (cleaned == airport_city or cleaned in airport_name):
            return iata

    return None


def fetch_flights(dep_iata: str, arr_iata: str, flight_date: str | None = None, limit: int = 5) -> list[dict]:
    """Fetches flight data from the AviationStack API."""
    if not API_KEY:
        return []

    params = {
        "access_key": API_KEY,
        "dep_iata": dep_iata,
        "arr_iata": arr_iata,
        "limit": limit
    }
    if flight_date:
        params["flight_date"] = flight_date

    try:
        response = requests.get(BASE_URL, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.RequestException:
        # Fallback to HTTPS if HTTP failed or vice versa
        alt_url = BASE_URL.replace("http://", "https://") if BASE_URL.startswith("http://") else BASE_URL.replace("https://", "http://")
        try:
            response = requests.get(alt_url, params=params, timeout=12)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception:
            return []


def format_flight_info(flights: list[dict], dep_iata: str, arr_iata: str) -> str:
    """Formats raw flight JSON into a clear, structured markdown response."""
    origin_airport = AIRPORTS.get(dep_iata, {}).get("name", dep_iata)
    dest_airport = AIRPORTS.get(arr_iata, {}).get("name", arr_iata)

    if not flights:
        return (
            f"No live scheduled flights found directly between **{dep_iata}** ({origin_airport}) "
            f"and **{arr_iata}** ({dest_airport}).\n"
            f"- Route: {dep_iata} -> {arr_iata}\n"
            f"- Note: Flights on this route may require a layover or schedule verification with major carriers."
        )

    output = [
        f"### Flights from {dep_iata} ({origin_airport}) to {arr_iata} ({dest_airport})\n"
    ]

    for i, flight in enumerate(flights, 1):
        airline = (flight.get("airline") or {}).get("name") or "Unknown Airline"
        flight_iata = (flight.get("flight") or {}).get("iata") or "N/A"
        status = (flight.get("flight_status") or "scheduled").capitalize()

        dep_info = flight.get("departure") or {}
        arr_info = flight.get("arrival") or {}

        dep_time = dep_info.get("scheduled", "N/A")
        arr_time = arr_info.get("scheduled", "N/A")
        dep_terminal = dep_info.get("terminal")
        arr_terminal = arr_info.get("terminal")

        terminal_str = ""
        if dep_terminal or arr_terminal:
            terminal_str = f" | Terminals: Dep {dep_terminal or 'Main'} -> Arr {arr_terminal or 'Main'}"

        output.append(
            f"**{i}. {airline} ({flight_iata})** - Status: `{status}`\n"
            f"   - Departure: {dep_time} ({dep_iata})\n"
            f"   - Arrival: {arr_time} ({arr_iata}){terminal_str}\n"
        )

    return "\n".join(output)


@tool
def search_flights(
    destination: str | None = None,
    origin: str | None = None,
    query: str | None = None,
    date: str | None = None
) -> str:
    """Search for flights given either a natural language travel query or explicit origin/destination.
    
    Accepts natural language queries such as:
    - 'plan a 7 day napal treap from bangladesh'
    - 'flights from dhaka to nepal'
    - 'flight to tokyo from bangladesh'
    - 'trip to dubai'
    
    Or explicit parameters:
    - destination: 'Kathmandu', origin: 'Dhaka'
    """
    raw_query = query or destination or ""
    if not raw_query:
        return "Please provide a destination or travel query (e.g. 'plan a 7 day napal treap from bangladesh')."

    # If the user passed a natural language sentence, extract origin, destination, and date
    extracted_origin, extracted_dest, extracted_date = extract_locations_from_query(raw_query)

    # Priority for Origin:
    # 1. Explicit origin inside the user query (e.g. "india to london" -> "india")
    # 2. Automatically detected user location passed from frontend/system (e.g. "Bangladesh")
    # 3. System default origin ("DAC")
    effective_origin = extracted_origin or origin or DEFAULT_ORIGIN
    effective_dest = extracted_dest or destination or raw_query
    effective_date = date or extracted_date

    dep_iata = resolve_airport_code(effective_origin)
    arr_iata = resolve_airport_code(effective_dest)

    if not dep_iata:
        return f"Could not determine airport code for origin: '{effective_origin}'. Please provide a city, country, or 3-letter IATA code."

    if not arr_iata:
        return f"Could not determine airport code for destination: '{effective_dest}'. Please provide a city, country, or 3-letter IATA code."

    flights = fetch_flights(dep_iata, arr_iata, flight_date=effective_date)
    return format_flight_info(flights, dep_iata, arr_iata)
