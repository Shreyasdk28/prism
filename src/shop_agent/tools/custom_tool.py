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
