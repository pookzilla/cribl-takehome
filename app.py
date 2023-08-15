import os
from flask import Flask
from views.v1.logs import logs_view
import socket


def create_app():
    app = Flask(__name__)
    app.register_blueprint(logs_view)

    # let the host name be configurable for cases where gethostname doesn't
    # provide the value you're hoping for
    # let the dir from which files are loaded be configurable to facilitate
    # testing
    app.config.update({
        "HOST_NAME": os.environ.get('HOST_NAME', socket.gethostname()),
        "ROOT_DIR": os.environ.get("ROOT_DIR", "/var/log/")
    })

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
