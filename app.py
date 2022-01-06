from datetime import timedelta
from flask_jwt_extended.utils import get_jwt
import pymongo
from flask import Flask, json, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
import configparser

import datetime

# 20220104 Add feature:revoke token
'''
import redis
ACCESS_EXPIRES = timedelta(hours=1)
'''

config = configparser.ConfigParser()
config.read('config.ini')

# locl MongoDB create db and collection
client = MongoClient(config.get('mongodb-url','url_pro'))
db = client["app_database"]
user = db["User"]

# Create a Flask app and configure it
app = Flask(__name__)
jwt = JWTManager(app)

# JWT config
app.config["JWT_SECRET_KEY"] = "hello-my-name-is-leo"

# 20220104 Add feature:revoke token
'''
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
'''

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    test = user.find_one({"email":email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
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
    
    test = user.find_one({"email":email,"password":password})
    if test:
        access_token = create_access_token(identity=email)
        user.update_one({"email":email,"password":password},{'$set':{"last_login":datetime.datetime.now()}})
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

@app.route("/dashboard")
@jwt_required()
def dashboard():
    return jsonify(message="Welcome!")

if __name__ == "__main__":
    app.run()