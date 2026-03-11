import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

load_dotenv("secrets.env")  # or ".env"

COLLECTION = "kaustubh_portfolio"

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

client.create_payload_index(
    collection_name=COLLECTION,
    field_name="verified",
    field_schema=PayloadSchemaType.BOOL,
)

print("Payload index created for 'verified'")
