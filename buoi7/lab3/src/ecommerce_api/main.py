import os

from flask import Flask, jsonify
from flask_smorest import Api
from sqlalchemy import text

from ecommerce_api.Extensions import db, migrate
from ecommerce_api.api.Orders import order_bp
from ecommerce_api.api.Products import product_bp
from ecommerce_api.exceptions.handlers import register_error_handlers
from ecommerce_api.logging_config import configure as configure_logging
from ecommerce_api.models.Order import Order
from ecommerce_api.models.OrderItem import OrderItem
from ecommerce_api.models.Product import Product


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///ecommerce.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        API_TITLE="Ecommerce API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )
    if test_config:
        app.config.update(test_config)

    configure_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.register_blueprint(product_bp)
    api.register_blueprint(order_bp)
    register_error_handlers(app)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    @app.get("/ready")
    def ready():
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db.session.rollback()
            return jsonify({"status": "not_ready"}), 503
        return jsonify({"status": "ready"}), 200

    return app
