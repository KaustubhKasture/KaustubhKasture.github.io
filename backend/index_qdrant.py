import os, uuid, requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv

# Load your secrets file
load_dotenv("secrets.env")  # filename must match exactly

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),  # matches env key
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION = "kaustubh_portfolio"

# Create collection if not exists
if not client.collection_exists(COLLECTION):
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

# Read knowledge file (test chunk)
with open("knowledge.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Call Jina Embeddings API
resp = requests.post(
    "https://api.jina.ai/v1/embeddings",
    headers={
        "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
        "Content-Type": "application/json"
    },
    json={
        "model": "jina-embeddings-v3",
        "input": [text]
    },
    timeout=10
)

j = resp.json()
print("Jina API Response:", j)

if "data" not in j or not j["data"]:
    raise RuntimeError("No embeddings returned. Check your Jina API key or input.")

vec = j["data"][0]["embedding"]

# Upsert into Qdrant
client.upsert(
    COLLECTION,
    [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={"text": text, "verified": True}
        )
    ]
)

print("Indexed into Qdrant!")
