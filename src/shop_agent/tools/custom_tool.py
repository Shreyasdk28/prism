from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os

# ------------------------------
# Tool 1: Amazon Search by Query
# ------------------------------

class AmazonSearchInput(BaseModel):
    query: str = Field(..., description="The search term to look up on Amazon.")

def search_amazon(query: str) -> str:
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "amazon_search",
        "q": query,
        "api_key": os.environ["AMAZON_SEARCH_API_KEY"]
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code} - {response.text}"

class AmazonSearchTool(BaseTool):
    name: str = "Amazon Search"
    description: str = "Searches Amazon for product listings based on a given query."
    args_schema: Type[BaseModel] = AmazonSearchInput

    def _run(self, query: str) -> str:
        return search_amazon(query)

# ------------------------------------
# Tool 2: Amazon Product Details by ASIN
# ------------------------------------

class AmazonProductDetailInput(BaseModel):
    asin: str = Field(..., description="The ASIN of the product to retrieve details for.")

def get_amazon_product_details(asin: str) -> str:
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "amazon_product",
        "asin": asin,
        "api_key": os.environ["AMAZON_SEARCH_API_KEY"]
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code} - {response.text}"

class AmazonProductDetailTool(BaseTool):
    name: str = "Amazon Product Detail"
    description: str = "Fetches detailed product info from Amazon using the ASIN."
    args_schema: Type[BaseModel] = AmazonProductDetailInput

    def _run(self, asin: str) -> str:
        return get_amazon_product_details(asin)
