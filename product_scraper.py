from langchain.tools import tool
import random
import json


@tool("product_scraper", return_direct=True)
def product_scraper_tool(url_list: list | str):
    """
    Takes a list of product URLs and returns mock product details like specs and reviews.
    The tool is robust: it accepts either a Python list of URLs or a JSON/stringified list.
    Example inputs:
      - ["https://example.com/product1"]
      - "[\"https://example.com/product1\"]"
      - "https://example.com/product1"
    """
    # Normalize input: accept stringified JSON lists or single URL strings
    if isinstance(url_list, str):
        try:
            parsed = json.loads(url_list)
            if isinstance(parsed, list):
                url_list = parsed
            else:
                # parsed to something else (e.g., a single string); wrap it
                url_list = [str(parsed)]
        except json.JSONDecodeError:
            # Not JSON — treat as a single URL string
            url_list = [url_list]

    # Ensure url_list is a list
    if not isinstance(url_list, list):
        url_list = [url_list]
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

    results = []
    for url in url_list:
        results.append({
            "url": url,
            "specs": random.choice(mock_specs),
            "reviews": random.sample(mock_reviews, 2),
        })

    return results