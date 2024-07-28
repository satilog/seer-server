import os
import uuid

import numpy as np
import requests
from flask import current_app
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from app.utils.resources import global_resources

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Initialize embedding model
model = SentenceTransformer("sentence-transformers/clip-ViT-B-32")

# In-memory data store for indexing
index = []


def get_embedding(text):
    response = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return response.data[0].embedding


# def embed_text(text):
#     return model.encode(text).tolist()


def store_vectors(documents):
    index = global_resources.index
    upserts = []

    for doc in documents:
        embedding = get_embedding(doc["text"])
        upsert_doc = {
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "url": doc["url"],
                "text": doc["text"],
                "task_id": doc["task_id"],
            },
        }
        upserts.append(upsert_doc)

    if upserts:
        index.upsert(vectors=upserts)


def search_with_query(query):
    query_embedding = get_embedding(query)

    # Assuming Pinecone index is set up and initialized
    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
    return results


def stringify_metadata(metadata):
    import datetime
    import json

    def stringify_value(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, (datetime.date, datetime)):
            return value.isoformat()
        else:
            return str(value)

    for key, value in metadata.items():
        if isinstance(value, list):
            metadata[key] = [stringify_value(item) for item in value]
        else:
            metadata[key] = stringify_value(value)

    return metadata
