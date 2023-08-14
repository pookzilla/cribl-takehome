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

### GET v1/logs/{file}?search={keywords}&limit={entry_count}
Retrieve the contents of the specified file located within /var/log.  The contents will be returned in reverse chronological order with most recent events appearing first.

|argument|description|required|default|
|--------|-----------|--------|-------|
| file | the filename within /var/log to retrieve | yes | n/a|
| keywords | the keywords that must be present within a log line in order for it to be returned | no | return all lines |
| entry_count | the maximum number of entries to return | no | all |

| header | description | required | default |
|--------|-------------|----------|---------|
| Accept | The desired format for the response.  | no | defaults to application/json. Accepted values are `application/json` and `text/html` |

#### Results
200 OK:

```json
{
    "file":"system.log",
    "host":"Kosm.local,
    "logs": [
        ...
    ]
}
``````

#### Examples

TBD
