import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from app.routes.common_routes import common_routes
from app.utils.resources import global_resources


def create_app():
    app = Flask(__name__)
    # app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    # app.config["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
    # app.config["PINECONE_INDEX_NAME"] = os.getenv("PINECONE_INDEX_NAME")

    with app.app_context():
        # Initialize Pinecone and load embedding models
        global_resources.init_pinecone()
        global_resources.load_embedding_models()

    app.register_blueprint(common_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
