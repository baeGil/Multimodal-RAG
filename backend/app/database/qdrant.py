from qdrant_client import QdrantClient
from qdrant_client.http import models
import os

# create qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# create colections 

collection_config = models.VectorParams(
    size=384,
    distance=models.Distance.COSINE
)
