from flask import Flask
from pymongo import MongoClient
from .config.config import config
from flask_cors import CORS

config_name = 'production'
app = Flask(__name__)
app.config.from_object(config[config_name])
cors = CORS(app,origins=app.config['ORIGINS'])#, supports_credentials=True)

# MongoDB create db and collection
client = MongoClient(app.config['DATABASE_URL'])
db = client["app_database"]
user = db["User"]
