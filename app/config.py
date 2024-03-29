import os

class DevelopmentConfig:
    DATABASE_URL = 'mongodb://localhost:27017/'
    SWAGGER_HOST = 'localhost:5000'
    REDISDB_URL = 'redis://:@localhost:6379'
    UPLOAD_FOLDER = 'app/data/'
    DOWNLOAD_FOLDER = 'data/'
    ORIGINS = 'http://localhost:5004'

class DevelopmentConfigDocker:
    DATABASE_URL = 'mongodb://mongo-dev:27017/'
    SWAGGER_HOST = 'localhost:5000'
    REDISDB_URL = 'redis://:@redis-dev:6379'
    UPLOAD_FOLDER = 'app/data/'
    DOWNLOAD_FOLDER = 'data/'
    ORIGINS = 'http://localhost:5004'

class ProductionConfig:
    DATABASE_URL = 'mongodb+srv://leolee:su3cp3gj94@cluster0.slk3i.mongodb.net/app_database?retryWrites=true&w=majority'
    SWAGGER_HOST = 'data-analyze-ml-toolset-backend.azurewebsites.net'
    REDISDB_URL = 'redis://:@redis-dev:6379'
    UPLOAD_FOLDER = '/home/app/data/'
    DOWNLOAD_FOLDER = '/home/app/data/'
    ORIGINS = 'https://leoinventorydemo.azurewebsites.net'

config = {
    'development' : DevelopmentConfig,
    'development-docker' : DevelopmentConfigDocker,
    'production' : ProductionConfig,
}