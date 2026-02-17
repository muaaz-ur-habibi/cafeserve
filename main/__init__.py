from flask import Flask
from flask_cors import CORS

def BUILD():
    app = Flask(__name__)
    from .routes import routes

    app.register_blueprint(routes)

    CORS(app)
    return app