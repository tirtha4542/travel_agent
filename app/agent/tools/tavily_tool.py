import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=api_key) if api_key else None


def tavily_search(query: str) -> str:
    """Executes a real-time web search with graceful error fallback."""
    if not client:
        return "Tavily search is not configured (missing TAVILY_API_KEY)."
    try:
        response = client.search(
            query=query,
            max_results=5
        )
        result = []
        for i, r in enumerate(response.get("results", []), 1):
            title = r.get("title", "unknown")
            url = r.get("url", "")
            snippet = r.get("content", "").strip()
            if len(snippet) > 300:
                snippet = snippet[:300].rsplit(" ", 1)[0] + "..."
            # Protect against Windows cp1252 terminal encoding crashes from scraped symbols
            title = title.encode("ascii", errors="replace").decode("ascii")
            snippet = snippet.encode("ascii", errors="replace").decode("ascii")
            result.append(f"{i}. **{title}**\n  {url}\n  {snippet}")
        return "\n\n".join(result)
    except Exception as e:
        return f"Real-time web search temporarily unavailable ({str(e)}). Please refer to official booking links."
