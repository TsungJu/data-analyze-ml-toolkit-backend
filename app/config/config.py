import os

class DevelopmentConfig:
    DATABASE_URL = 'mongodb://localhost:27017/'
    SWAGGER_HOST = 'localhost:5000'
    REDIS_URL = 'redis://:@localhost:6379'

class ProductionConfig:
    DATABASE_URL = 'mongodb+srv://leolee:su3cp3gj94@cluster0.slk3i.mongodb.net/app_database?retryWrites=true&w=majority'
    SWAGGER_HOST = 'leonardapi.herokuapp.com'
    REDIS_URL = os.environ['REDIS_URL']

config = {
    'development' : DevelopmentConfig,
    'production' : ProductionConfig,
}