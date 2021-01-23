# FLASK USER MANAGEMENT APP

## Create and Activate Virtual Environment

```shell
python3 -m venv venv
source venv/bin/activate
```

## Install dependencies

```shell
pip install -r requirements.txt
```

NOTE: To run test/website, create a local .env file with the following values
`SECRET_KEY={ANY-STRING-HARD-QUESS}`

## To run tests

```shell
pytest
```

## To run website

```shell
export FLASK_APP=app
flask run
```
