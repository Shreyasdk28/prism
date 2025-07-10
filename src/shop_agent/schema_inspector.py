import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# ✅ Set these to match your setup
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "shopping_episodes"

# 🔌 Connect to Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# 🧠 Inspect payload schema
try:
    collection = client.get_collection(COLLECTION_NAME)
    schema = collection.payload_schema

    if not schema:
        print("⚠️ No payload schema (no indexes found).")
    else:
        print(f"📦 Payload schema for '{COLLECTION_NAME}':\n")
        for field, index_info in schema.items():
            print(f"- {field}: {index_info.data_type} (params: {getattr(index_info, 'params', None)})")
except Exception as e:
    print(f"❌ Error: {e}") 