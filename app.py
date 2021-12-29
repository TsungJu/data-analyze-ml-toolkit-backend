import pymongo
from flask import Flask, json, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# locl MongoDB create db and collection
client = MongoClient(config.get('mongodb-url','url'))
db = client["app_database"]
user = db["User"]

# Create a Flask app and configure it
app = Flask(__name__)
jwt = JWTManager(app)

# JWT config
app.config["JWT_SECRET_KEY"] = "hello-my-name-is-leo"

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
        user_info = dict(first_name=first_name,last_name=last_name,email=email,password=password)
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
        return jsonify(message="Login Succeeded!",access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401

@app.route("/dashboard")
@jwt_required()
def dashboard():
    return jsonify(message="Welcome!")

if __name__ == "__main__":
    app.run(host="localhost", debug=True)