from flask import Flask
from pymongo import MongoClient
from .config.config import config

config_name = 'development'
app = Flask(__name__)
app.config.from_object(config[config_name])

# MongoDB create db and collection
client = MongoClient(app.config['DATABASE_URL'])
db = client["app_database"]
user = db["User"]
