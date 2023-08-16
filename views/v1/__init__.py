
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash


"""
Support hard-coded credential authorization.  In the real deal maybe we'd be
considering host password verification + permissions checks.  This could go
right down to the file level but for the sake of this demo we'll KISS.
"""
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("cribl")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
