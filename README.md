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

### Run application

```shell
export FLASK_APP=app
flask run
```

### **ps: Perform databases migration**

To run application for the first time, perform database migration using the commands below at the root folder

```shell
flask db init
flask db migrate
flask db upgrade
```
