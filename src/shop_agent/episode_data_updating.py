import os
from uuid import uuid4
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# ✅ Set your environment variables or directly provide them here
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ✅ Initialize Qdrant Cloud client
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# ✅ Sentence embedding model (384-dim for MiniLM)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Collection name
collection_name = "shopping_episodes"

# Sample input
user_id = "cloud_test_user_01"
query = "affordable ANC wireless earbuds"
vector = embedder.encode(query).tolist()

# Prepare payload
payload = {
    "user_id": user_id,
    "query": query,
    "item_details": "Noise Air Buds Pro 2, ANC, budget under ₹2500",
    "final_items": "Noise Air Buds Pro 2",
    "timestamp": datetime.now().isoformat(),
    "description": "Cloud test: Inserting sample wireless earbuds shopping episode"
}

# ✅ Insert the vector point
client.upsert(
    collection_name=collection_name,
    points=[{
        "id": str(uuid4()),
        "vector": vector,
        "payload": payload
    }]
)

print("✅ Successfully inserted test data into Qdrant Cloud")
