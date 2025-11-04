import os
from dotenv import load_dotenv
from serpapi.google_search import GoogleSearch
from langchain_core.tools import tool

# Load .env file
load_dotenv()

# Access the key
api_key = os.getenv("SERP_API")

# Function to search for a product and return results usinf SerpAPI
@tool
def web_search_tool(query: str) -> str:
    """
    Perform a Google search using SerpAPI.

    Args:
        query (str): The search query.

    Returns:
        str: A formatted list of top search results (title and link).
    """

    print(f"Searching for: {query}")

    params = {
    "engine": "google",
    "q": query,
    "api_key": api_key,
    "num": 3
    }

    search = GoogleSearch(params)
    results = search.get_dict() or {}
    # print(results) # debug

    # organic_results may not always be present depending on SerpAPI response or errors.
    organic_results = results.get("organic_results") or []

    output = []
    if isinstance(organic_results, list) and organic_results:
        for r in organic_results:
            # append only title and link from results (guarding missing keys)
            title = r.get("title") or r.get("position") or "(no title)"
            link = r.get("link") or r.get("url") or "(no link)"
            output.append(f"{title} — {link}")
    else:
        # Fallback: try to extract from other common fields if organic_results absent
        # e.g., answer_box, knowledge_graph, or top_result
        if isinstance(results, dict):
            # try answer box
            ab = results.get("answer_box") or results.get("top_result") or {}
            title = None
            link = None
            if isinstance(ab, dict):
                title = ab.get("title") or ab.get("snippet")
                link = ab.get("link") or ab.get("url")
            if title or link:
                output.append(f"{title or '(no title)'} — {link or '(no link)'}")

    print("Search results:", output)
    return "\n".join(output[:3])


