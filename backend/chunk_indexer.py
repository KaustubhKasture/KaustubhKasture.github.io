import os, uuid, requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, Match
from dotenv import load_dotenv

# Load API keys
load_dotenv("secrets.env")

# Connect to Qdrant Cloud
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION = "kaustubh_portfolio"

# Recreate collection fresh for chunked vectors (only for testing, remove later if not resetting)
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)

client.create_collection(
    COLLECTION,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)

# Create index for verified field so filter queries work
client.create_payload_index(
    collection_name=COLLECTION,
    field_name="verified",
    field_schema="bool"
)

# Read your knowledge
with open("knowledge.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Split by meaning-based sections
def semantic_chunk_split(text):
    chunks = []
    current = []
    for line in text.split("\n"):
        if line.startswith("[") and line.endswith("]"):
            if current:
                chunks.append("\n".join(current))
                current = []
        current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks

chunks = semantic_chunk_split(raw_text)

print(f"Total semantic chunks created: {len(chunks)}")

# Embed and upsert each chunk
for i, chunk in enumerate(chunks):
    print(f"\n🔹 Processing chunk {i+1}/{len(chunks)}")
    print(chunk[:120], "...")  # preview start of chunk
    
    try:
        r = requests.post(
            "https://api.jina.ai/v1/embeddings",
            headers={
                "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={"model": "jina-embeddings-v3", "input": [chunk]},
            timeout=10,
        ).json()

        if "data" not in r or not r["data"]:
            print("❗ No embedding returned, skipping this chunk.")
            continue

        vec = r["data"][0]["embedding"]

        # Metadata extraction
        section = "general"
        for line in chunk.split("\n"):
            if line.startswith("[") and line.endswith("]"):
                section = line.strip("[]").lower()
                break

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={"text": chunk, "verified": True, "section": section}
        )

        client.upsert(COLLECTION, [point])
        print(f"✔ Chunk indexed in section: {section}")

    except Exception as e:
        print(f"Embedding failed for this chunk: {str(e)}")

print("\n🚀 All done! Knowledge indexed into Qdrant Cloud in semantic sections.")
