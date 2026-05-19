"""Entry point for running the chat connector with Flask's development server."""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
