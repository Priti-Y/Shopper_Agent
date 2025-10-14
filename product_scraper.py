from langchain.tools import tool
import random

@tool("product_scraper_tool", return_direct=True)
def product_scraper_tool(url_list: list):
    """
    Takes a list of product URLs and returns mock product details like specs and reviews.
    Example input: ["https://example.com/product1"]
    """
    mock_specs = [
        {"brand": "LeatherLux", "material": "Genuine Leather", "color": "Brown", "price": "$85"},
        {"brand": "EcoTrend", "material": "Vegan Leather", "color": "Black", "price": "$70"},
        {"brand": "UrbanStyle", "material": "Canvas", "color": "Grey", "price": "$45"}
    ]

    mock_reviews = [
        "Excellent quality and fast delivery!",
        "Good value for money, but packaging could improve.",
        "Stylish design, perfect for daily use."
    ]
    print(f"***************************{url_list}")
    results = []
    for url in url_list:
        results.append({
            "url": url,
            "specs": random.choice(mock_specs),
            "reviews": random.sample(mock_reviews, 2)
        })
     

    return results