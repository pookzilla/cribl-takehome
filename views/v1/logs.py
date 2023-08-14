from flask import Blueprint, current_app, jsonify, request
from flask_accept import accept_fallback
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from services.log_services import LogService

logs_view = Blueprint('logs', __name__)
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("cribl")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logs_view.route('/v1/logs/<file>')
@accept_fallback
@auth.login_required
def logs_json(file):
    return jsonify(generate_logs(file))


@logs_json.support("text/html")
@auth.login_required
def logs_html(file):

    result = generate_logs(file)
    return f"\
        <h1>{result.host}:/var/log/{result.file}</h1>\
        {'<br>'.join(result.logs)}\
    "


def generate_logs(file):
    log_service = LogService()

    return log_service.get_logs(**collect_args(file, request.args))


def collect_args(file, args):
    search = args.get("search", default=None, type=str)
    limit = args.get("limit", default=None, type=int)

    return {
        "file": file,
        "search": search,
        "limit": limit
    }
