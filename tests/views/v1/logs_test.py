import base64
import collections.abc
import json

import pytest
from app import create_app


@pytest.fixture()
def application():
    application = create_app()
    application.config.update({
        "TESTING": True,
        "HOST_NAME": "pytest"
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
    response = client.get(
        '/v1/logs/system.log',
        headers={
            "Accept": "application/json"
        }
    )
    assert response.status_code == 401


def test_get_logs_success__default_json(client):
    response = client.get(
        '/v1/logs/system.log',
        headers={
            "Accept": "*/*",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    result = json.loads(response.data.decode('utf-8'))
    assert result["file"] == "system.log"
    assert result["host"] == "pytest"
    assert isinstance(result["logs"], collections.abc.Sequence)


def test_get_logs_success__json(client):
    response = client.get(
        '/v1/logs/system.log',
        headers={
            "Accept": "application/json",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    result = json.loads(response.data.decode('utf-8'))
    assert result["file"] == "system.log"
    assert result["host"] == "pytest"
    assert isinstance(result["logs"], collections.abc.Sequence)


def test_get_logs_success__html(client):
    response = client.get(
        '/v1/logs/system.log',
        headers={
            "Accept": "text/html",
            "Authorization": auth_header
        }
    )
    assert response.status_code == 200
    assert response.content_type is not None \
        and response.content_type.startswith("text/html")
