import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from models import Product

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
    #print(results) #immersive_products
    organic_results = results["organic_results"]
    #prod_results = results["immersive_products"]
    products = []
    for r in organic_results[:num_results]:
        try:
            # Map API fields to Pydantic model fields
            product = Product(
                product_name=r.get("title"),
                price=float(r.get("price", 0)),  # fallback 0 if missing
                link=r.get("link")
            )
            products.append(product)
        except Exception as e:
            print(f"Skipping invalid result: {r} - {e}")
    return products

if __name__ == "__main__":
    # search for "iPhone 16 Pro" and get top 2 results
    products = search_product("iPhone 16 Pro", 2)
    for p in products:
        print(p.json()) 