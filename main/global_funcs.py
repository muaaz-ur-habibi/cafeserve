from flask import Blueprint, Flask
import importlib.util
from sys import modules
from flask_cors import CORS
from sys import executable, argv
from os import execv

def restart_server():
    execv(executable, ['python'] + argv)

def BUILD():
    app = Flask(__name__)
    from .routes import routes, cf

    app.register_blueprint(routes)
    CORS(app)

    register_addons(cf, app)

    return app

def register_addons(config, app:Flask):
    for a in config["addons"]:
        print("Trying to register addon", a['name'])
        try:
            spec = importlib.util.spec_from_file_location(a["name"].lower(), a["filename"])
            module = importlib.util.module_from_spec(spec)

            modules[a["name"].lower()] = module

            spec.loader.exec_module(module)

            addon = module.addon

            if hasattr(module, "init_addon"):
                module.init_addon(config["server"]["database"])

            if isinstance(addon, Blueprint):
                addon.template_folder = f"{str(a["filename)"]).rsplit("/", maxsplit=1)[0]}/{addon.template_folder}"
                print(addon.template_folder)
                app.register_blueprint(addon)
                print(f"{a['name']} registered")
        
        except FileNotFoundError:
            print(f"{a['name']} not found")