import json
from flask import Blueprint, abort, request, current_app
from flask_accept import accept_fallback
from views.v1 import auth

from services.dispatch_services import DispatchService

views = Blueprint('dispatch', __name__)

"""
Helper functions
"""
def generate_logs(app, file):
    dispatch_service = DispatchService()

    return dispatch_service.get_logs(app, **collect_args(file, request.args))


def collect_args(file, args):
    """
    Process and validate all provided query arguments (if any.)
    """
    servers_str = args.get("servers", default=None, type=str)
    servers = None
    if servers_str is not None:
        servers = servers_str.split(',')
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
        "servers": servers,
        "search": search,
        "limit": limit,
        "auth": request.headers["Authorization"]
    }


"""
Our supported routes.
"""
@views.route('/v1/dispatch/<path:file>')
@accept_fallback
@auth.login_required
async def dispatch_json(file):
    app = current_app._get_current_object()
    result = generate_logs(app, file)

    def json_wrapper():
        yield "["
        first = True
        for log in result:
            if not first:
                yield ','

            first = False
            yield json.dumps(log)
        yield "]"
    return json_wrapper(), {"Content-Type": "application/json"}
