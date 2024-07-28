from flask import Blueprint

main = Blueprint("main", __name__)

from .common_routes import common_routes

# Register blueprints
main.register_blueprint(common_routes, url_prefix="/api/v1")
