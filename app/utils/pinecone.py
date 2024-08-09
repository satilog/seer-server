import os
from urllib.parse import urlparse
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
    index = global_resources.index
    query_embedding = get_embedding(query)

    # Assuming Pinecone index is set up and initialized
    print(query_embedding)
    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
    # print(results)
    return results

# function to check if there is data of the same domain

def is_data_of_same_domain_as_pinecone_index(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    try:
        # Create a dummy vector with the correct dimension (1536 in this case)
        dummy_vector = [0] * 1536
        
        # Retrieve top_k results from Pinecone index using the correct dimensional vector
        results = global_resources.index.query(vector=dummy_vector, top_k=100, include_metadata=True)
        print(len(results['matches']), " results retrieved")
        
        # Check if any of the retrieved results have the same domain in their metadata
        for match in results['matches']:
            stored_domain = urlparse(match['metadata']['url']).netloc
            if stored_domain == domain:
                return True
        return False
    except Exception as e:
        print(e)
        return False
    

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
