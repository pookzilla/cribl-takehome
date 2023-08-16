import html
import json
from flask import Blueprint, abort, request
from flask_accept import accept_fallback
from views.v1 import auth
from services.log_services import LogService

views = Blueprint('logs', __name__)


"""
Helper functions
"""
def generate_logs(file):
    log_service = LogService()

    return log_service.get_logs(**collect_args(file, request.args))


def collect_args(file, args):
    """
    Process and validate all provided query arguments (if any.)
    """
    search_str = args.get("search", default=None, type=str)
    search = None
    if search_str is not None:
        search = search_str.split(',')
    limit_str = args.get("limit", default=None)
    limit = None
    if limit_str is not None:
        if not limit_str.isdigit() or (int(limit_str) < 1):
            abort(400, 'limit must be a positive integer if provided')
        else:
            limit = int(limit_str)  # if we arent a number we arent anything

    return {
        "file": file,
        "search": search,
        "limit": limit
    }


"""
Our supported routes.
"""
@views.route('/v1/logs/<path:file>')
@accept_fallback
@auth.login_required
def logs_json(file):
    result = generate_logs(file)
    if not result:
        abort(404)

    def json_wrapper():
        yield "["
        first = True
        for line in result.logs:
            if not first:
                yield ','

            first = False
            yield json.dumps({
                "host": result.host,
                "file": result.file,
                "log": line
            })
        yield "]"
    return json_wrapper(), {"Content-Type": "application/json"}


@logs_json.support("application/stream+json")
@auth.login_required
def logs_json_stream(file):
    result = generate_logs(file)
    if not result:
        abort(404)

    def json_wrapper():

        for line in result.logs:
            yield json.dumps({
                "host": result.host,
                "file": result.file,
                "log": line
            }) + "\n"
    return json_wrapper(), {"Content-Type": "application/stream+json"}

@logs_json.support("text/html")
@auth.login_required
def logs_html(file):

    result = generate_logs(file)
    if not result:
        abort(404)

    def html_wrapper():
        yield f"<h1>{result.host}:/var/log/{result.file}</h1>\n"
        for line in result.logs:
            # do some basic html encoding
            escaped = html.escape(line) \
                .replace(' ', '&nbsp;') \
                .replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
            yield f"{escaped}<br>\n"

    return html_wrapper(), {"Content-Type": "text/html"}
