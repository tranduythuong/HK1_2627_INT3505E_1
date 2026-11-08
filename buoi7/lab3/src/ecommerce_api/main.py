from flask import Flask
from flask_smorest import Api

from ecommerce_api.Extensions import db, migrate
from ecommerce_api.api.Products import product_bp
from ecommerce_api.exceptions.handlers import register_error_handlers
from ecommerce_api.models.Product import Product

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["API_TITLE"] = "Ecommerce API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_JSON_PATH"] = "openapi.json"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.register_blueprint(product_bp)
    register_error_handlers(app)

    return app
