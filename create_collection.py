from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, KeywordIndexParams

import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "shopping_episodes"

# Step 1: Create or recreate collection
if client.collection_exists(collection_name):
    print(f"🔁 Collection '{collection_name}' already exists. Recreating it.")
    client.delete_collection(collection_name=collection_name)

print(f"🛠️ Creating collection '{collection_name}'...")
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Step 2: Create payload index for `user_id`
print(f"🔑 Creating payload index for `user_id`...")
client.create_payload_index(
    collection_name=collection_name,
    field_name="user_id",
    field_schema=KeywordIndexParams(type="keyword")  # ✅ Proper usage for filterable field
)

print("✅ Collection and index created successfully.")
