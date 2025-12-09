from flask import Blueprint, request, render_template, redirect, url_for, send_file
from random import randint

from .usermanager import UsersManager
from .database import DatabaseManager, ScriptsManager

from sys import argv

if len(argv) < 2:
    print('USAGE:\n' \
          '     python cafeserve.py [database location]')
    
    exit(0)

routes = Blueprint("routes", "routes")

CODE:int = randint(100, 999)

print("The server code is", CODE)

um = UsersManager()
dm_base_dir = argv[1]
dm = DatabaseManager(dm_base_dir)
sm = ScriptsManager()

@routes.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home.html")
    
    elif request.method == "POST":
        name = request.form.get("username")
        code = request.form.get("code")

        if int(code) == CODE:
            um.add_user(name)
            return redirect(f'{name}/dashboard')
        
        else:
            return render_template("home.html", ERROR="Invalid code, please try again")
    
@routes.route("/<name>/dashboard")
def dashboard(name):
    if um.is_logged_in(name):
        if request.method == "GET":
            return render_template("dashboard.html", name=name)
        
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))


@routes.route("/<name>/files/<direc>", methods=["GET", "POST"])
def files(name, direc):
    dm.rebuild_nodes(dm.ROOT_NODE)
    if um.is_logged_in(name):
        if request.method == "GET":
            current_list = dm.get_database_list(dm.get_node_from_path(dm.urlify(direc, False)))
            return render_template(
                "files.html",
                name=name,
                li=current_list,
                direc=direc,
                preview=False
                )
        
        elif request.method == "POST":
            _file = request.files.get("file-upload")
            folder = request.files.getlist("folder-upload")

            if _file:
                dm.add_path(f"{dm.urlify(direc, False)}/{_file.filename}", True, _file.stream.read())
                dm.add_node(_file.filename, dm.urlify(direc, False), _file.stream.read())

            if folder:
                for f in folder:
                    if f.filename != '':
                        dm.add_path(f"{dm.urlify(direc, False)}/{f.filename}", True, f.stream.read())
                        dm.add_node(f.filename, dm.urlify(direc, False), f.stream.read())

            current_list = dm.get_database_list(dm.get_node_from_path(dm.urlify(direc, False)))
            return render_template(
                "files.html",
                name=name,
                li=current_list,
                direc=direc,
                preview=False
                )
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
@routes.route("/<name>/preview_file/<path>")
def preview_file(name, path):
    if um.is_logged_in(name):
        if request.method == "GET":
            c = dm.get_file_contents(dm.urlify(path, False))
            if c[:3] != "UG_":
                return render_template(
                    "preview_file.html", contents=c, fpath=path, name=name
                )
            
            else:
                c = c.split("UG_")[-1].split("/")[0]
                if c == 'video':
                    path = dm.urlify(path, False)
                    return render_template(
                        "video_player.html", path=path, name=name
                    )
    
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
@routes.route("/<name>/get_file/<path>")
def get_file(name, path):
    if um.is_logged_in(name):
        return send_file(dm.urlify(path, False))
    

@routes.route("/<name>/scripts", methods=["GET", "POST"])
def scripts(name):
    if um.is_logged_in(name):
        if request.method == "GET":
            return render_template("scripts.html", scripts=sm.scripts_list, name=name)
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
@routes.route("/<name>/add_script/<path>")
def add_script(name, path):
    if um.is_logged_in(name):
        if request.method == "GET":
            sm.add_script(dm.urlify(path, False))

            return redirect(url_for('routes.scripts', name=name))

    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
@routes.route("/<name>/run_script/<script_id>", methods=["GET", "POST"])
def run_script(name, script_id):
    if um.is_logged_in(name):
        if request.method == 'GET':
            return render_template("run_script.html", result=("", "", 0))
        
        else:
            run_command = request.form.get("run-command")
            s = sm.get_script_by_ID(int(script_id))
            res = sm.run_script(s, run_command)

            return render_template("run_script.html", result=res)
        
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))