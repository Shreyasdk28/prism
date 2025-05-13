# # tools/crawl4ai_tool.py

# from crewai.tools import BaseTool
# from typing import Type, List, Dict, Any, Optional
# from pydantic import BaseModel, Field
# from crawl4ai import AsyncWebCrawler
# import asyncio
# import json

# class Crawl4AILinksInput(BaseModel):
#     links_file: Optional[str] = Field(None, description="Path to JSON file containing list of URLs to scrape.")
#     links: Optional[List[str]] = Field(None, description="Direct list of product page URLs to scrape.")
#     max_pages: int = Field(1, description="How many pagination steps to follow on each URL, if applicable.")

# class Crawl4AILinkScraperTool(BaseTool):
#     name: str = "Crawl4AI Link Scraper"
#     description: str = (
#         "Reads a JSON file or list of product-page URLs, crawls each with Crawl4AI, "
#         "extracts detailed product info (title, price, specifications, reviews, image links) and returns combined JSON list."
#     )
#     args_schema: Type[BaseModel] = Crawl4AILinksInput

#     def _run(self, links_file: Optional[str] = None, links: Optional[List[str]] = None, max_pages: int = 1) -> str:
#         # Load links from JSON file if provided
#         urls: List[str] = []
#         if links_file:
#             try:
#                 with open(links_file, 'r', encoding='utf-8') as f:
#                     urls = json.load(f)
#             except Exception as e:
#                 return json.dumps({"error": f"Failed to load links_file: {e}"})
#         if links:
#             urls = (urls or []) + links
#         if not urls:
#             return json.dumps({"error": "No URLs provided to scrape."})
#         # Run crawler
#         return asyncio.run(self._crawl_and_extract(urls, max_pages))

#     async def _crawl_and_extract(self, urls: List[str], max_pages: int) -> str:
#         # Define extraction hooks for product detail page
#         extraction_hooks = {
#             "product": {
#                 "selector": "body",  # entire page - we will extract fields inside
#                 "fields": {
#                     "title": {"selector": "h1, .product-title", "default": None},
#                     "price": {"selector": "._30jeq3, .price, .offer-price", "default": None},
#                     "specifications": {"selector": ".specs-list, .product-specs", "attr": "innerText", "default": None},
#                     "rating": {"selector": "._3LWZlK, .rating", "default": None},
#                     "review_count": {"selector": ".reviews-count, #acrCustomerReviewText", "default": None},
#                     "image_url": {"selector": "img._396cs4, img.product-image", "attr": "src", "default": None}
#                 }
#             }
#         }

#         all_details: List[Dict[str, Any]] = []
#         async with AsyncWebCrawler() as crawler:
#             for url in urls:
#                 next_url = url
#                 for _ in range(max_pages):
#                     result = await crawler.arun(
#                         url=next_url,
#                         extraction_hooks=extraction_hooks
#                     )
#                     # parse extracted JSON content
#                     content = result.extracted_content or "{}"
#                     page_data = json.loads(content)
#                     detail = page_data.get("product") or {}
#                     # normalize any relative image/link fields
#                     if detail.get("image_url", "").startswith('/'):
#                         detail["image_url"] = crawler._normalize_url(next_url, detail["image_url"])
#                     detail["source_url"] = url
#                     all_details.append(detail)
#                     # pagination not typical on product page; break
#                     break
#         return json.dumps(all_details, ensure_ascii=False)



from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from serpapi import GoogleSearch
import os
import json

class GoogleShoppingInput(BaseModel):
    query: str = Field(..., description="The search query, e.g. 'wireless earphones under 1500 INR'")
    location: str = Field("India", description="Location to search from, e.g. 'India'")

class GoogleShoppingTool(BaseTool):
    name: str = "Google Shopping Tool"
    description: str = "Fetches shopping results using SerpAPI's Google Shopping engine based on query and location."
    args_schema: Type[BaseModel] = GoogleShoppingInput

    def _run(self, query: str, location: str = "India") -> str:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not serpapi_key:
            return "Error: SERPAPI_API_KEY not found in environment variables."

        params = {
            "engine": "google_shopping",
            "q": query,
            "location": location,
            "hl": "en",
            "gl": "in",  # India-specific results
            "api_key": serpapi_key
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            products = results.get("shopping_results", [])
        except Exception as e:
            return f"Error fetching results: {str(e)}"

        clean_results = []

        for p in products:
            clean_results.append({
                "title": p.get("title"),
                "price": p.get("price"),
                "source": p.get("source"),
                "link": p.get("link"),
                "product_link": p.get("product_link"),
                "rating": p.get("rating"),
                "reviews": p.get("reviews"),
                "thumbnail": p.get("thumbnail"),
                "delivery": p.get("delivery"),
            })

        return json.dumps(clean_results, ensure_ascii=False, indent=2)
