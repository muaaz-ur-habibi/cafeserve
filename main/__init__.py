from flask import Flask

def BUILD():
    app = Flask(__name__)
    from .routes import routes

    app.register_blueprint(routes)

    return app