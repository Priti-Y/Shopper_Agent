from langchain.tools import tool
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import json

@tool("product_scraper", return_direct=True)
def product_scraper_tool(url_list: list | str):
    """
    Takes a list of product URLs and scrapes real-time product specifications and reviews.
    Works with Amazon, Flipkart, and generic e-commerce pages.
    Accepts either a Python list, a JSON list string, or a single URL string.

    Example inputs:
      - ["https://www.amazon.in/dp/B0C7S2FL8K/"]
      - "[\"https://www.flipkart.com/poco-x6-pro-5g/p/itm2c4f2561da8a0\"]"
      - "https://example.com/product1"
    """

    # --- Normalize input --- #
    if isinstance(url_list, str):
        try:
            parsed = json.loads(url_list)
            if isinstance(parsed, list):
                url_list = parsed
            else:
                url_list = [str(parsed)]
        except json.JSONDecodeError:
            url_list = [url_list]

    if not isinstance(url_list, list):
        url_list = [url_list]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    # --- Helper functions for known domains --- #
    def scrape_amazon(soup):
        specs, reviews = {}, []
        title = soup.find("span", {"id": "productTitle"})
        specs["Product Title"] = title.get_text(strip=True) if title else "N/A"

        # Product detail table
        detail_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
        if detail_table:
            for row in detail_table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    specs[th.get_text(strip=True)] = td.get_text(strip=True)

        # Additional feature bullets
        bullet_points = soup.select("#feature-bullets ul li span")
        if bullet_points:
            specs["Key Features"] = [b.get_text(strip=True) for b in bullet_points if b.get_text(strip=True)]

        # Customer reviews
        for r in soup.select(".review-text-content span"):
            text = r.get_text(strip=True)
            if text:
                reviews.append(text)
        return specs, reviews[:5]

    def scrape_flipkart(soup):
        specs, reviews = {}, []
        title = soup.find("span", {"class": "B_NuCI"})
        specs["Product Title"] = title.get_text(strip=True) if title else "N/A"

        # Product Specs table
        for row in soup.select("table._14cfVK tr"):
            tds = row.find_all("td")
            if len(tds) == 2:
                specs[tds[0].get_text(strip=True)] = tds[1].get_text(strip=True)

        # Feature list
        feature_list = soup.select("div._2418kt ul li")
        if feature_list:
            specs["Key Features"] = [li.get_text(strip=True) for li in feature_list if li.get_text(strip=True)]

        # Reviews
        for r in soup.select("div.t-ZTKy div"):
            txt = r.get_text(strip=True)
            if txt and len(reviews) < 5:
                reviews.append(txt)
        return specs, reviews

    def scrape_generic(soup):
        specs, reviews = {}, []
        title = soup.find(["h1", "h2"])
        specs["Product Title"] = title.get_text(strip=True) if title else "N/A"

        # Generic spec extraction
        for li in soup.find_all("li")[:10]:
            text = li.get_text(" ", strip=True)
            if ":" in text:
                k, v = text.split(":", 1)
                specs[k.strip()] = v.strip()

        # Extract paragraphs with 'review' or 'comment'
        for r in soup.find_all(class_=lambda c: c and "review" in c.lower()):
            txt = r.get_text(strip=True)
            if txt and len(reviews) < 5:
                reviews.append(txt)
        return specs, reviews

    # --- Main scraping logic --- #
    results = []
    for url in url_list:
        domain = urlparse(url).netloc.lower()
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                results.append({"url": url, "error": f"HTTP {resp.status_code}"})
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            if "amazon" in domain:
                specs, reviews = scrape_amazon(soup)
            elif "flipkart" in domain:
                specs, reviews = scrape_flipkart(soup)
            else:
                specs, reviews = scrape_generic(soup)

            results.append({
                "url": url,
                "specs": specs,
                "reviews": reviews if reviews else ["No reviews found."]
            })

        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })

    return results
