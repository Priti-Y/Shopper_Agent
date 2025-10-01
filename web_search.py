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
    results = search.get_dict()
    #print(results) #immersive_products
    organic_results = results["organic_results"]
    #prod_results = results["immersive_products"]

    output = []
    for r in organic_results:
        #append only title and link from results
        output.append(f"{r.get('title')} — {r.get('link')}")
    
    return "\n".join(output[:3])


