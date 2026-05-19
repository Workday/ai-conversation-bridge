"""Flask application factory for the chat connector."""

import logging

from flask import Flask

from app.config import Config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.debug = Config.DEBUG
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

    logging.basicConfig(level=logging.INFO)

    from app.routes import bp
    app.register_blueprint(bp)

    return app
