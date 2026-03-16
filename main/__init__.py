from flask import Flask
from flask_cors import CORS
from .global_funcs import register_addons

def BUILD():
    app = Flask(__name__)
    from .routes import routes, cf

    app.register_blueprint(routes)
    CORS(app)

    register_addons(cf, app)

    return app