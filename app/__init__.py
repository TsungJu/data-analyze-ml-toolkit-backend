from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from .config import config
from flask_cors import CORS
from datetime import timedelta
from flasgger import Swagger

config_name = 'production'
app = Flask(__name__)
app.config.from_object(config[config_name])

# JWT config
ACCESS_EXPIRES = timedelta(hours=1)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_SECRET_KEY"] = "LEONARD-JWT-SECRET-KEY"
jwt = JWTManager(app)

# CORS config
cors = CORS(app,origins=app.config['ORIGINS'])#, supports_credentials=True)

# Swagger config
swagger_template = dict(
    info = {
        'title':'flask jwt api Swagger UI Document',
        'version':'0.1',
        'description':'This document depicts a flask jwt api Swagger ui document.',
    },
    host = app.config['SWAGGER_HOST'],
    tags = [
        {
            'name':'User',
            'description':'User related Features'
        },
        {
            'name':'File',
            'description':'File related Features'
        },
        {
            'name':'Analyzing',
            'description':'Analyzing related Features'
        },
        {
            'name':'Modeling',
            'description':'Modeling related Features'
        }
    ],
    securityDefinitions = {
      'Bearer': {
        'type':'apiKey',
        'name':'Authorization',
        'in':'header'
      }
    }
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

# MongoDB create db and collection
client = MongoClient(app.config['DATABASE_URL'])
db = client["app_database"]
user = db["User"]
