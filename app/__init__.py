import os

from dotenv import load_dotenv

load_dotenv()

from flask import Blueprint, Flask, jsonify, request

from app.utils.crawler import get_crawl_status, start_crawl
from app.utils.pinecone import search_with_query
from app.utils.resources import global_resources

# def create_app():
#     app = Flask(__name__)
#     # app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
#     # app.config["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
#     # app.config["PINECONE_INDEX_NAME"] = os.getenv("PINECONE_INDEX_NAME")

#     with app.app_context():
#         # Initialize Pinecone and load embedding models
#         global_resources.init_pinecone()
#         global_resources.load_embedding_models()

#     from app.routes import main as main_blueprint

#     app.register_blueprint(main_blueprint)

#     from app.routes.common_routes import common_routes as common_blueprint

#     app.register_blueprint(common_blueprint, url_prefix="/api/v1/common")

#     return app

app = Flask(__name__)


@app.route("/crawl", methods=["POST"])
def crawl():
    data = request.json
    start_url = data.get("start_url")
    depth = data.get("depth", 2)  # Default depth is 2 if not provided

    response, status_code = start_crawl(start_url, depth)
    return jsonify(response), status_code


@app.route("/status", methods=["GET"])
def status():
    task_id = request.args.get("task_id")
    response, status_code = get_crawl_status(task_id)
    return jsonify(response), status_code


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")

    print(query)
    if not query:
        return jsonify({"error": "Query is required"}), 400

    results = search_with_query(query)
    return jsonify(results), 200


if __name__ == "__main__":
    app.run(debug=True)
