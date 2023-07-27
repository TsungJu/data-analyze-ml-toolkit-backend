from app import app
from .auth.auth import auth_blueprint
from .file.file import file_blueprint
from .analyzing.analyzing import analyzing_blueprint
from .modeling.modeling import modeling_blueprint
#from .predicting.predicting import predicting_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(file_blueprint)
app.register_blueprint(analyzing_blueprint)
app.register_blueprint(modeling_blueprint)
#app.register_blueprint(predicting_blueprint)

@app.cli.command()
def test():
    import unittest
    import sys

    tests = unittest.TestLoader().discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.errors or result.failures:
        sys.exit(1)
