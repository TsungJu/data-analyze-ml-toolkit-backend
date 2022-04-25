# Analyzing and Modeling RestAPI by flask-jwt-api

## What is it ?

This project uses the bearer token authorization by flask-jwt-api ,and provides RestAPI like this:

- User related feature like login、register、password forgot、password reset.

- File related feature like file upload、file list、file download、file delete.

- analyzing related feature like csv correlation analyze、csv info、histogram plot、diagram plot、scatter plot.

- modeling related feature like build linear regression、multiple regression、polynomial regression、decision tree.

## How to use ?

## Prerequisites

### Run mongodb locally:

$ `docker run -d --name mongodb-dev -p 27017:27017 mongo`

## Build and run me locally

Modify `app/__init__.py` variable `config_name` to `development`

### Windows:

$ `pip install -r requirements_win.txt`

$ `set FLASK_APP=main.py`

$ `flask run`

### Linux:

$ `pip install -r requirements.txt`

$ `export FLASK_APP=main.py`

$ `flask run`

### Swagger UI URL:

http://localhost:5000/apidocs/

### Run Unit Test:

$ `flask test`

### Coverage Test:

$ `coverage run -m flask test`

$ `coverage report -m`

### Export coverage test report:

$ `coverage html`
