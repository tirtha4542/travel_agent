import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def tavily_search(query: str) -> str:
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
