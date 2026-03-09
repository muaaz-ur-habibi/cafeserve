from flask import Flask, Blueprint
from flask_cors import CORS
import importlib.util
from sys import modules

def register_addons(config, app:Flask):
    for a in config["addons"]:
        spec = importlib.util.spec_from_file_location(a["name"].lower(), a["filename"])
        module = importlib.util.module_from_spec(spec)

        modules[a["name"].lower()] = module

        spec.loader.exec_module(module)

        addon = module.addon

        if isinstance(addon, Blueprint):
            app.register_blueprint(addon)
            print(f"{a['name']} registered")

def BUILD():
    app = Flask(__name__)
    from .routes import routes, cf

    app.register_blueprint(routes)
    CORS(app)

    register_addons(cf, app)

    return app