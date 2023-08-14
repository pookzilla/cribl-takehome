import os
from flask import Flask
from views.v1.logs import logs_view
import socket


def create_app():
    app = Flask(__name__)
    app.register_blueprint(logs_view)
    app.config.update({
        "HOST_NAME": os.environ.get('HOST_NAME', socket.gethostname())
    })

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
