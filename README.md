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
This project supports the following APIs:

### GET /v1/logs/{file}?search={search}&limit={limit}
Retrieve the contents of the specified file located within /var/log.  The contents will be returned in reverse chronological order with most recent events appearing first.

|argument|description|required|default|
|--------|-----------|--------|-------|
| file | the filename within /var/log to retrieve | yes | n/a|
| search | the comma separted list of keywords that must be present within a log line in order for it to be returned.  Provided any one of the keywords is present the line is returned | no | return all lines |
| limit | the maximum number of entries to return | no | all |

| header | description | required | default |
|--------|-------------|----------|---------|
| Accept | The desired format for the response.  | no | defaults to application/json. Accepted values are `application/json`, `application/stream+json` and `text/html` |
| Authorization | Basic auth header for access control.  For purposes of this demo, username `admin` and password `cribl` | yes | n/a |

#### General Comments
* utilizes python generator support within Flask to provide results asyncrhonously.  This is positive in terms of performance but detrimental in terms of error handling because if an error occurs somewhere after the headers have already been flushed to the client there is no way to mark the request as failed.  This could result in malformed json in the case of `application/json` requests.  This could possibly be mitigated by some form of multipart response or chunked transfer trailers but that's a non-trivial amount of work.
* only most basic of html support - curl is the queen!
* included auth checking but would need more in a production system.  Tying into the system user system and checking file permissions could be reasonable.

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

### GET /v1/dispatch/{file}?servers={servers}&search={search}&limit={limit}
Dispatch calls to a number of servers running the `/v1/logs/*` API, interleaving results from each in a roundrobin form.

|argument|description|required|default|
|--------|-----------|--------|-------|
| file | the filename within /var/log to retrieve | yes | n/a|
| servers| the comma-separated list of servers on which to call /v1/logs/{file} | yes | n/a |
| search | the comma separted list of keywords that must be present within a log line in order for it to be returned.  Provided any one of the keywords is present the line is returned | no | return all lines |
| limit | the maximum number of entries to return across all servers.  Ie: you will see at most `limit` results from any one server. | no | all |

| header | description | required | default |
|--------|-------------|----------|---------|
| Accept | The desired format for the response.  | no | defaults to application/json. Accepted values are `application/json` and `text/html` |
| Authorization | Basic auth header for access control.  For purposes of this demo, username `admin` and password `cribl`.  This header will be forwarded on to any of the servers in the dispatch list. | yes | n/a |

#### General Comments
* made assumptions that the results should be interleaved rather than held in a map keyed by hostname.  This better facilitates a streamed response IMO and is likely more in line with how you would be utilizing the API to track down issues across a cluster.  With introspection of the log line perhaps time-sorting would be possible.
* the complexities specific to using a python co-routine as a Flask generator _work_ in this demo though the implementation is not clean and only extensively tested in the case of the happy path.  This was my first time bridging that particular divide and I suspect there are ways to make the implementation cleaner.  I don't think there would be significant changes to the general shape of the solution rather a sprinking of `async` and `yield from` and removal of the dependency on a hand crafted `asyncio` event loop.
* kept the result format the same as with `/v1/logs/*` for ease of integration
* no pytests for this endpoint - figuring out the weirdness in turning a coroutine into a generator took more time than I had hoped.

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

Request the logs from two servers:

```bash
curl http://127.0.0.1:8080/v1/dispatch/wifi.log?servers=127.0.0.1:5000,127.0.0.1:5000
```

Note above those servers are the same - for the purposes of demonstration you can see that both are being called because events are effectively doubled, in sorted order, in this response.  Also note that if you are running this code via docker the port you request is not necessarily the same as the port you need to specify in the server list as that request will be made within the context of that container where the service port may differ from the exposed host port.