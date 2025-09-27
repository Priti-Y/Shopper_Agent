import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load .env file
load_dotenv()

# Access the key
api_key = os.getenv("SERP_API")

#  Function to search for a product and return results usinf SerpAPI
def search_product(product_searched, num_results):
    
    params = {
    "engine": "google",
    "q": product_searched,
    "api_key": api_key,
    "num": num_results
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results

if __name__ == "__main__":
    # Example usage
    results = search_product("iPhone 16 Pro", 5)
    organic_results = results["organic_results"]
    print(f"organic_results + {organic_results}")