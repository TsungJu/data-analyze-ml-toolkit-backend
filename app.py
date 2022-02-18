from datetime import timedelta
from distutils.command.upload import upload
# from flask_jwt_extended.utils import get_jwt
import pymongo
from flask import Flask, json, jsonify, request, redirect, url_for, flash, send_from_directory, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, decode_token
from pymongo import MongoClient
import configparser
import bcrypt
from jwt.exceptions import DecodeError, InvalidTokenError
import datetime
from flasgger import Swagger
# For file upload
from werkzeug.utils import secure_filename
import os
import pandas as pd

# For file upload
UPLOAD_FOLDER = 'C:/Users/leolee/Documents/flask-jwt-api/data'
ALLOWED_EXTENSIONS = {'txt','pdf','png','jpg','jpeg', 'gif','csv'}

# 20220104 Add feature:revoke token
# import redis
ACCESS_EXPIRES = timedelta(hours=1)

config = configparser.ConfigParser()
config.read('config.ini')
# locl MongoDB create db and collection
client = MongoClient(config.get('mongodb-url','url_pro'))
db = client["app_database"]
user = db["User"]

# Create a Flask app and configure it
app = Flask(__name__)
jwt = JWTManager(app)
swagger_template = dict(
    info = {
        'title':'flask jwt api Swagger UI Document',
        'version':'0.1',
        'description':'This document depicts a flask jwt api Swagger ui document.',
    },
    host = 'leonardapi.herokuapp.com',
    tags = [
        {
            'name':'User',
            'description':'User related Features'
        }
    ]
)
swagger_config = {
    'headers':[],
    'specs':[
        {
            'endpoint':'flask_jwt_api_swagger_ui',
            'route':'/flask_jwt_api_swagger_ui.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path':'/flasgger_static',
    'swagger_ui': True,
    'specs_route':'/apidocs/'
}
swagger = Swagger(app,template=swagger_template,config=swagger_config)

# JWT config
app.config["JWT_SECRET_KEY"] = "hello-my-name-is-leo"
# For flash session
app.secret_key = "my-name-is-leo"

# For file upload
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# 20220104 Add feature:revoke token
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET','POST'])
@jwt_required()
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            # flash('No file part')
            return redirect(request.url)
    
        file = request.files['file']
        # app.logger.info(test)
        #df = pd.read_csv(file)
        #print(df)
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            token = request.headers['Authorization'].split(' ')[1]
            email = decode_token(token)['sub']
            first_name=user.find_one({"email":email})['first_name']
            path= 'data/'+first_name+'/'
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path,filename))
            return jsonify(message=filename+" Upload successfully"), 201
            #return redirect(url_for('uploaded_file',filename=filename))
    
    return render_template('upload.html')
'''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
'''
@app.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download(filename):
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    print(decode_token(token))
    first_name=user.find_one({"email":email})['first_name']
    path= 'data/'+first_name
    return send_from_directory(path,filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete(filename):
    token = request.headers['Authorization'].split(' ')[1]
    email = decode_token(token)['sub']
    first_name=user.find_one({"email":email})['first_name']
    path= 'data/'+first_name+'/'
    if os.path.exists(path):
        os.remove(path+filename)
    return jsonify(message=filename+" Delete successfully"), 200

@app.route('/register', methods=['POST'])
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

@app.route('/login', methods=['POST'])
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
        return jsonify(message="Login Successfully",access_token=access_token), 200
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

@app.route('/forgot', methods=['POST'])
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

@app.route('/reset',methods=['POST'])
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

@app.route('/dashboard')
@jwt_required()
def dashboard():
    return jsonify(message="Welcome!")

# if __name__ == "__main__":
#    app.run()