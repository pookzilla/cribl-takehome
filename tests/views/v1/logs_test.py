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


def test_get_logs_success_json(client):
    response = client.get(
        '/v1/logs/system.log',
        headers={"Accept": "application/json"}
    )
    result = json.loads(response.data.decode('utf-8'))
    assert result["file"] == "system.log"
    assert result["host"] == "pytest"
    assert isinstance(result["logs"], collections.abc.Sequence)
