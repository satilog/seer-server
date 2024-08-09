import os
import time

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

class GlobalResources:
    def __init__(self):
        self.index = None
        self.embedding_model = None

    def init_pinecone(self):
        pinecone = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

        indexes = pinecone.list_indexes()
        print(indexes)

        index_name = os.getenv("PINECONE_INDEX_NAME")
        print(index_name)
        # pinecone.init(api_key=current_app.config["PINECONE_API_KEY"])
        # index_name = current_app.config["PINECONE_INDEX_NAME"]

        # if index_name not in pinecone.list_indexes()['indexes']:
        #     pinecone.create_index(name=index_name, dimension=1536, metric="cosine")
        if not any(index["name"] == index_name for index in indexes):
            pinecone.create_index(name=index_name, dimension=1536, metric="cosine")
            print(f"Index '{index_name}' created.")
        else:
            print(f"Index '{index_name}' already exists.")

        self.index = pinecone.Index(index_name)

    # Can use this if openai embeddings get expensive
    def load_embedding_models(self):
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(
                "sentence-transformers/clip-ViT-B-32"
            )


# Instantiate the global resources
global_resources = GlobalResources()
