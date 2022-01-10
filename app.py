from datetime import timedelta
from flask_jwt_extended.utils import get_jwt
import pymongo
from flask import Flask, json, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, decode_token
from pymongo import MongoClient
import configparser
import bcrypt
from jwt.exceptions import DecodeError, InvalidTokenError
import datetime
# from flask_mail import Mail
# For flask logging
from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# 20220104 Add feature:revoke token
# import redis
ACCESS_EXPIRES = timedelta(hours=1)

config = configparser.ConfigParser()
config.read('config.ini')
# locl MongoDB create db and collection
client = MongoClient(config.get('mongodb-url','url_dev'))
db = client["app_database"]
user = db["User"]

# Create a Flask app and configure it
app = Flask(__name__)
jwt = JWTManager(app)
# mail = Mail(app)

# JWT config
app.config["JWT_SECRET_KEY"] = "hello-my-name-is-leo"

# 20220104 Add feature:revoke token
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    test = user.find_one({"email":email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = bcrypt.hashpw((request.form["password"]).encode('utf-8'), bcrypt.gensalt())
        created_on = datetime.datetime.now()
        user_info = dict(first_name=first_name,last_name=last_name,email=email,password=password,created_on=created_on,last_login=created_on)
        user.insert_one(user_info)
        return jsonify(message="User added sucessfully"), 201

@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = user.find_one({"email":email})
    app.logger.info(test)
    if bcrypt.checkpw(password.encode('utf-8'), test['password']):
        access_token = create_access_token(identity=email)
        user.update_one({"email":email},{'$set':{"last_login":datetime.datetime.now()}})
        return jsonify(message="Login Succeeded!",access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401

# 20220104 Add feature:revoke token
'''
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost",port=6379,db=0,decode_responses=True
)

# 20220104 Add feature:revoke token
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None

# 20220104 Add feature:revoke token
@app.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(message="Access token revoked")
'''

@app.route("/forgot", methods=["POST"])
def forgot_password():
    email = request.form["email"]
    test = user.find_one({"email":email})
    if not test:
        return jsonify(message="email not Exist"), 404
    else:
        reset_token = create_access_token(identity=email)
        return jsonify(reset_token=reset_token), 201

@app.route("/reset",methods=['POST'])
def reset_password():
    try:
        new_password = bcrypt.hashpw((request.form["new_password"]).encode('utf-8'), bcrypt.gensalt())
        reset_token = request.form["reset_token"]
        email = decode_token(reset_token)['sub']
        user.update_one({"email":email},{'$set':{"password":new_password}})
        return jsonify(message="Reset password success!"), 201
    except DecodeError:
        raise DecodeError("DecodeError")
    except InvalidTokenError:
        raise InvalidTokenError("InvalidTokenError")

@app.route("/dashboard")
@jwt_required()
def dashboard():
    return jsonify(message="Welcome!")

if __name__ == "__main__":
    app.run()