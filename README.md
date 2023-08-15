# Cribl Takehome Assignment


## Running

Running this project will require that Docker be installed.

To build the project:
```bash
docker build --tag khorne/cribl .
```

To run the project:
```bash
export HOST_NAME=$HOST
export HOST_PORT=8080 
docker run -p "$HOST_PORT:8080" -e "HOSTNAME=$HOST_NAME" khorne/cribl
```

## Testing

To run the unit tests for this project you will require valid python 3.9 installation or virtual environment:

```bash
export PYTHONPATH=. pytest
pytest -rP
```

## API
This project supports the following API:

### GET v1/logs/{file}?search={search}&limit={limit}
Retrieve the contents of the specified file located within /var/log.  The contents will be returned in reverse chronological order with most recent events appearing first.

|argument|description|required|default|
|--------|-----------|--------|-------|
| file | the filename within /var/log to retrieve | yes | n/a|
| search | the comma separted list of keywords that must be present within a log line in order for it to be returned.  Provided any one of the keywords is present the line is returned | no | return all lines |
| limit | the maximum number of entries to return | no | all |

| header | description | required | default |
|--------|-------------|----------|---------|
| Accept | The desired format for the response.  | no | defaults to application/json. Accepted values are `application/json` and `text/html` |
| Authorization | Basic auth header for access control.  For purposes of this demo, username `admin` and password `cribl` | yes | n/a |

#### Results
200 OK:

```json
[
    {
        "file":"system.log",
        "host":"Kosm.local",
        "log": "message"
    },
    ...
]
```

400 Bad Request:

* returned if limit is supplied and it isnt a positive integer


#### Examples

Request an entire log in html format:

```bash
curl http://127.0.0.1:8080/v1/logs/dpkg.log -H "Accept: text/html" -H "Authorization: Basic YWRtaW46Y3JpYmw="
```

Request the lastest 10 log lines:

```bash
curl http://127.0.0.1:8080/v1/logs/dpkg.log\?limit\=10 -H "Authorization: Basic YWRtaW46Y3JpYmw=" | jq .
```
