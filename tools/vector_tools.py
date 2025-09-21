import os
from typing import Optional, ClassVar
from pydantic import ConfigDict, PrivateAttr
from crewai.tools import BaseTool
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    KeywordIndexParams
)
from sentence_transformers import SentenceTransformer


class ShoppingMemorySearchTool(BaseTool):
    name: str = "shopping_memory_search"
    description: str = (
        "Semantic search over shopping session memory.\n"
        "Input:\n"
        "- query: str → product or item description (e.g., 'wireless earbuds')\n"
        "- user_id: str → filter results to a specific user\n"
        "Returns: a list of relevant past shopping episodes"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Class-level constants
    collection_name: ClassVar[str] = "shopping_episodes"
    vector_dim: ClassVar[int] = 384
    score_threshold: ClassVar[float] = 0.75
    limit: ClassVar[int] = 5

    # Private attributes
    _qdrant: QdrantClient = PrivateAttr()
    _embedder: SentenceTransformer = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self._embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Ensure keyword index on user_id
        try:
            schema = self._qdrant.get_collection(self.collection_name).payload_schema or {}
            if "user_id" not in schema:
                print(f"🔧 Creating keyword index on 'user_id'")
                self._qdrant.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="user_id",
                    field_schema=KeywordIndexParams(type="keyword")
                )
        except Exception as e:
            print(f"⚠️ Index check failed: {e}")

    def _run(self, query: str, user_id: Optional[str] = None) -> list:
        try:
            vector = self._embedder.encode(query).tolist()

            search_filter = None
            if user_id:
                search_filter = Filter(
                    must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
                )

            results = self._qdrant.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=self.limit,
                with_payload=True,
                score_threshold=self.score_threshold,
                query_filter=search_filter
            )

            if not results:
                return [{"status": "no_results", "message": "No matches found."}]

            return [
                {
                    "status": "success",
                    "user_id": r.payload.get("user_id"),
                    "query": r.payload.get("query"),
                    "item_details": r.payload.get("item_details"),
                    "final_items": r.payload.get("final_items"),
                    "timestamp": r.payload.get("timestamp"),
                    "description": r.payload.get("description"),
                    "score": r.score
                }
                for r in results
            ]

        except Exception as e:
            return [{"status": "error", "message": str(e)}]
