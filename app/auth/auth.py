from flask import jsonify, request, url_for, render_template
from flask_jwt_extended import jwt_required, create_access_token, decode_token, get_jwt
import bcrypt
from jwt.exceptions import DecodeError, InvalidTokenError
import datetime
from .. import app, jwt, user
from flask import Blueprint

auth_blueprint = Blueprint('auth_blueprint', __name__)

import redis

@auth_blueprint.route('/api/register', methods=['POST'])
def register():
    """Endpoint for user register
    This is using docstrings for specifications.
    ---
    tags:
      - 'User'
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
      - name: first_name
        in: formData
        type: string
        required: true
      - name: last_name
        in: formData
        type: string
        required: true
    definitions:
      register_successfully_message:
        type: object
        properties:
          message:
            type: string
    responses:
      201:
        description: User register successfully message
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "User Register Successfully" }
    """
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
        return jsonify(message="User Register Successfully"), 201

@auth_blueprint.route('/api/login', methods=['POST'])
def login():
    """Endpoint for user login
    This is using docstrings for specifications.
    ---
    tags:
      - 'User'
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    definitions:
      login_successfully_message:
        type: object
        properties:
          message:
            type: string
          access_token:
            type: string
    responses:
      200:
        description: User login successfully message
        schema:
          $ref: '#/definitions/login_successfully_message'
        examples:
          application/json: { "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0NTA3NjUxMywianRpIjoiZDg3ODIyNzUtYWNjNC00NGNmLTgwZjYtMTVlM2QwMjQ1NzkyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImUyODUxNzFAaG90bWFpbC5jb20iLCJuYmYiOjE2NDUwNzY1MTMsImV4cCI6MTY0NTA4MDExM30.RC3kwHfQOXjL4WbWU2BL2W-82kP4BLsJsAKK35zflmI", "message": "Login Successfully" }
    """
    if request.is_json:
        email = request.json["username"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = user.find_one({"email":email})
    if bcrypt.checkpw(password.encode('utf-8'), test['password']):
        access_token = create_access_token(identity=email)
        user.update_one({"email":email},{'$set':{"last_login":datetime.datetime.now()}})
        return jsonify(message="Login Successfully",access_token=access_token), 200
    else:
        return jsonify(message="Bad Email or Password"), 401

# 20220704 Add Feature:revoke token
#jwt_redis_blocklist = redis.StrictRedis(
#    host="localhost",port=6379,db=0,decode_responses=True
#)
jwt_redis_blocklist = redis.Redis.from_url(app.config['REDISDB_URL'])

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None

@auth_blueprint.route("/api/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """Endpoint for user logout
    This is using docstrings for specifications.
    ---
    tags:
      - 'User'
    security:
      - Bearer: []
    responses:
      200:
        description: User logout successfully message
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Access token revoked" }
    """
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    return jsonify(message="Access token revoked")

@auth_blueprint.route('/api/forgot', methods=['POST'])
def forgot_password():
    """Endpoint for user forgot password
    This is using docstrings for specifications.
    ---
    tags:
      - 'User'
    parameters:
      - name: email
        in: formData
        type: string
        required: true
    definitions:
      reset_token_message:
        type: object
        properties:
          reset_token:
            type: string
    responses:
      404:
        description: Email not exist message
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "email not Exist" }
      201:
        description: Email exist response reset token
        schema:
          $ref: '#/definitions/reset_token_message'
        examples:
          application/json: { "reset_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0NTA3NjUxMywianRpIjoiZDg3ODIyNzUtYWNjNC00NGNmLTgwZjYtMTVlM2QwMjQ1NzkyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImUyODUxNzFAaG90bWFpbC5jb20iLCJuYmYiOjE2NDUwNzY1MTMsImV4cCI6MTY0NTA4MDExM30.RC3kwHfQOXjL4WbWU2BL2W-82kP4BLsJsAKK35zflmI" }
    """
    email = request.form["email"]
    test = user.find_one({"email":email})
    if not test:
        return jsonify(message="email not Exist"), 404
    else:
        reset_token = create_access_token(identity=email)
        return jsonify(reset_token=reset_token), 201

@auth_blueprint.route('/api/reset',methods=['POST'])
def reset_password():
    """Endpoint for user reset password
    This is using docstrings for specifications.
    ---
    tags:
      - 'User'
    parameters:
      - name: new_password
        in: formData
        type: string
        required: true
      - name: reset_token
        in: formData
        type: string
        required: true
    responses:
      201:
        description: Reset password success
        schema:
          $ref: '#/definitions/register_successfully_message'
        examples:
          application/json: { "message": "Reset password success" }
    """
    try:
        new_password = bcrypt.hashpw((request.form["new_password"]).encode('utf-8'), bcrypt.gensalt())
        reset_token = request.form["reset_token"]
        email = decode_token(reset_token)['sub']
        user.update_one({"email":email},{'$set':{"password":new_password}})
        return jsonify(message="Reset password success"), 201
    except DecodeError:
        raise DecodeError("DecodeError")
    except InvalidTokenError:
        raise InvalidTokenError("InvalidTokenError")

@auth_blueprint.route('/dashboard')
def dashboard():
    return jsonify(message="Welcome!")
