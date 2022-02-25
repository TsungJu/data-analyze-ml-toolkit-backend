# flask-jwt-api practice

This is flask-jwt-api practice.

[ Prerequisites ]

Run mongodb locally:

$ `docker run -d --name mongodb-dev -p 27017:27017 mongo`

[ Build and run me ]

Modify `app/__init__.py` variable `config_name` to `development`

Windows:

$ `pip install -r requirements_win.txt`

$ `set FLASK_APP=main.py`

$ `flask run`

Linux:

$ `pip install -r requirements.txt`

$ `export FLASK_APP=main.py`

$ `flask run`

Swagger UI URL:

http://localhost:5000/apidocs/

Run Unit Test:

$ `flask test`

Coverage Test:

$ `coverage run -m flask test`

$ `coverage report -m`

Export coverage test report:

$ `coverage html`
