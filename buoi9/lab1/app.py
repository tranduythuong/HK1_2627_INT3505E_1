"""Flask app demonstrating URI path versioning with separate blueprints."""

from flask import Flask

from blueprints.v1 import v1_blueprint
from blueprints.v2 import v2_blueprint


def create_app() -> Flask:
    app = Flask(__name__)
    @app.errorhandler(404)
    def handle_404(error):
        return {"error": "Resource not found"}, 404
    app.register_blueprint(v1_blueprint, url_prefix="/api/v1")
    app.register_blueprint(v2_blueprint, url_prefix="/api/v2")
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
