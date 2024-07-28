from flask import Blueprint, jsonify, request

from app.utils.crawler import get_crawl_status, start_crawl
from app.utils.pinecone import search_with_query

common_routes = Blueprint("common_routes", __name__)


@common_routes.route("/crawl", methods=["POST"])
def crawl():
    data = request.json
    start_url = data.get("start_url")
    depth = data.get("depth", 2)  # Default depth is 2 if not provided

    response, status_code = start_crawl(start_url, depth)
    return jsonify(response), status_code


@common_routes.route("/status", methods=["GET"])
def status():
    task_id = request.args.get("task_id")
    response, status_code = get_crawl_status(task_id)
    return jsonify(response), status_code


@common_routes.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    results = search_with_query(query)
    return jsonify(results), 200
