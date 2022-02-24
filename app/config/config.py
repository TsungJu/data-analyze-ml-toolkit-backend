
class DevelopmentConfig:
    DATABASE_URL = 'mongodb://localhost:27017/'
    SWAGGER_HOST = 'localhost:5000'

class ProductionConfig:
    DATABASE_URL = 'mongodb+srv://leolee:su3cp3gj94@cluster0.slk3i.mongodb.net/app_database?retryWrites=true&w=majority'
    SWAGGER_HOST = 'leonardapi.herokuapp.com'

config = {
    'development' : DevelopmentConfig,
    'production' : ProductionConfig,
}