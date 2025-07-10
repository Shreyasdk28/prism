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
    
from typing import Optional
from pydantic import ConfigDict
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
from uuid import uuid4
from typing import List, Type

from pydantic import BaseModel

class QdrantUpsertInput(BaseModel):
    user_id: str
    query: str
    item_details: str
    final_items: List[str]
    timestamp: str
    description: str

class QdrantCustomUpsertTool(BaseTool):
    name: str = "qdrant_upsert_tool"
    description: str = (
        "Upserts a shopping episode into the Qdrant vector DB using a local embedding model. "
        "Input should be a dict with: user_id, query, item_details, final_items, timestamp."
    )
    args_schema: Type[BaseModel] = QdrantUpsertInput 

    # Allow QdrantClient and SentenceTransformer as arbitrary types for Pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)

    qdrant: Optional[QdrantClient] = None
    collection: Optional[str] = None
    embedder: Optional[SentenceTransformer] = None

    def __init__(self):
        super().__init__()
        self.qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection = "shopping_episodes"
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim embeddings
        # self.ensure_collection(vector_size=384)

    # def ensure_collection(self, vector_size: int):
    #     existing_collections = self.qdrant.get_collections().collections
    #     if self.collection not in existing_collections:
    #         self.qdrant.recreate_collection(
    #             collection_name=self.collection,
    #             vectors_config={"size": vector_size, "distance": "Cosine"},
    #         )

    def _run(
        self,
        user_id: str,
        query: str,
        item_details: str,
        final_items: str,
        timestamp: str,
        description: str,
        **kwargs
    ) -> str:

        if not user_id or not query or not timestamp:
            return "Error: 'user_id', 'query' and 'timestamp' are required fields."

        vector = self.embedder.encode(query).tolist()

        point = {
            "id": str(uuid4()),  # Generate a unique ID for the point
            "vector": vector,
            "payload": {
                "user_id": user_id,
                "query": query,
                "item_details": item_details,
                "final_items": final_items,
                "timestamp": timestamp,
                "description": description,
            },
        }

        self.qdrant.upsert(collection_name=self.collection, points=[point])

        return "Data upserted to Qdrant successfully"
