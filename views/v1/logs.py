from flask import Blueprint, jsonify, request
from flask_accept import accept_fallback

from services.log_services import LogService

logs_view = Blueprint('logs', __name__)


@logs_view.route('/v1/logs/<file>')
@accept_fallback
def logs(file):
    log_service = LogService()

    return jsonify(log_service.get_logs(**collect_args(file, request.args)))


@logs.support("text/html")
def logs_html(file):
    log_service = LogService()

    result = log_service.get_logs(**collect_args(file, request.args))

    return f"\
        <h1>{result.host}:/var/log/{result.file}</h1>\
        {'<br>'.join(result.logs)}\
    "


def collect_args(file, args):
    search = args.get("search", default=None, type=str)
    limit = args.get("limit", default=None, type=int)

    return {
        "file": file,
        "search": search,
        "limit": limit
    }
