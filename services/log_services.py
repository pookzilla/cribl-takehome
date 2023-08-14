from models.log_models import LogResult
from flask import current_app


def sanitize_file(file):
    # TODO: ensure they aren't trying directory navigation trickery
    return file


class LogService():

    def __init__(self):
        self.hostname = current_app.config["HOST_NAME"]

    def get_logs(self, file, search=None, limit=None):
        file = sanitize_file(file)
        return LogResult(file, self.hostname, ["first", "second", "third"])
