import base64
import collections.abc
import json

import pytest
from app import create_app


@pytest.fixture(scope="session")
def log_dir(tmp_path_factory):
    log_content = """log 1
log 2
log 3
log 4
log 5
log 6
log 7
log 8
log 9
log 10
"""
    log_dir = tmp_path_factory.mktemp("logs")
    fn = log_dir / "test.log"
    f = open(fn, "a")
    f.write(log_content)
    f.close()

    return str(log_dir)


@pytest.fixture()
def application(log_dir):
    application = create_app()
    application.config.update({
        "TESTING": True,
        "HOST_NAME": "pytest",
        "ROOT_DIR": log_dir
    })

    yield application


@pytest.fixture()
def client(application):
    return application.test_client()


@pytest.fixture()
def runner(application):
    return application.test_cli_runner()


auth_header = f"Basic {base64.b64encode(str.encode('admin:cribl')).decode()}"


def test_get_logs_failure__auth(client):
    """
    Verifies request generate a 401 if an auth header isnt supplied
    """
    response = client.get(
        '/v1/logs/system.log?limit=10',
        headers={
            "Accept": "application/json"
        }
    )
    assert response.status_code == 401


def test_get_logs_success__default_content_type_json(client):
    """
    Verifies that if you make a request for a valid log without any parameters
    and without specifying an explicit content type the entire log is returned
    in json format in the correct order.
    """
    response = client.get(
        '/v1/logs/test.log',
        headers={
            "Accept": "*/*",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    result = json.loads(response.data.decode('utf-8'))
    assert isinstance(result, collections.abc.Sequence)
    assert len(result) == 10
    assert result[0]["log"] == "log 10"
    assert result[len(result) - 1]["log"] == "log 1"
    for record in result:
        print(json.dumps(record))
        assert record['host'] == 'pytest'
        assert record['file'] == 'test.log'
        assert record['log'].startswith("log ")


def test_get_logs_success__json(client):
    """
    Verifies that if you make a request for a valid log without any parameters
    and specifying json content type the entire log is returned in json format
    in the correct order.
    """
    response = client.get(
        '/v1/logs/test.log',
        headers={
            "Accept": "application/json",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    result = json.loads(response.data.decode('utf-8'))
    assert isinstance(result, collections.abc.Sequence)
    assert len(result) == 10
    assert result[0]["log"] == "log 10"
    assert result[len(result) - 1]["log"] == "log 1"
    for record in result:
        assert record['host'] == 'pytest'
        assert record['file'] == 'test.log'
        assert record['log'].startswith("log ")


def test_get_logs_success__limited_bigger_than_file(client):
    """
    Verifies that if you make a request for a valid log with a limit greater
    than the length of the file and specifying json content type the entire log
    is returned in json format in the correct order.
    """
    response = client.get(
        '/v1/logs/test.log?limit=15',
        headers={
            "Accept": "application/json",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    result = json.loads(response.data.decode('utf-8'))
    assert isinstance(result, collections.abc.Sequence)
    assert len(result) == 10
    assert result[0]["log"] == "log 10"
    assert result[len(result) - 1]["log"] == "log 1"
    for record in result:
        assert record['host'] == 'pytest'
        assert record['file'] == 'test.log'
        assert record['log'].startswith("log ")


def test_get_logs_success__limited(client):
    """
    Verifies that if you make a request for a valid log with a limit smaller
    than the length of the file and specifying json content type appropriate
    section of the log is returned in json format in the correct order.
    """
    response = client.get(
        '/v1/logs/test.log?limit=5',
        headers={
            "Accept": "application/json",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    result = json.loads(response.data.decode('utf-8'))
    assert isinstance(result, collections.abc.Sequence)
    assert len(result) == 5
    assert result[0]["log"] == "log 10"
    assert result[len(result) - 1]["log"] == "log 6"
    for record in result:
        assert record['host'] == 'pytest'
        assert record['file'] == 'test.log'
        assert record['log'].startswith("log ")


def test_get_logs_success__html(client):
    """
    Verifies that if you make a request for a valid log without any parameters
    and specifying html content type the entire log is returned in html format
    in the correct order.
    """
    response = client.get(
        '/v1/logs/test.log',
        headers={
            "Accept": "text/html",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type is not None \
        and response.content_type.startswith("text/html")
    assert response.data != ''
