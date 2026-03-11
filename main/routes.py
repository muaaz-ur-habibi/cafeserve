from flask import Blueprint, request, render_template, redirect, url_for, send_file
from random import randint

from .usermanager import UsersManager
from .database import DatabaseManager
from .server import get_server_stats, get_camera_feed
from .confighandler import Config

from datetime import datetime, timedelta

routes = Blueprint("routes", "routes")

CODE:int = randint(100, 999)

print("The server code is", CODE)

cf = Config("config.json").get_config()

um = UsersManager()
dm_base_dir = cf['server']['database']
dm = DatabaseManager(dm_base_dir)

ANNOUNCEMENTS_LIST:list[(str, int, datetime)] = []

# ------------------------------------- API ROUTES --------------------------------
@routes.route("/api/get_server_stats")
def api_get_server_stats():
    return get_server_stats(dm.BASE_DIR)

@routes.route("/api/get_users_count")
def api_get_users_count():
    return {'users_count': um.users_count}

@routes.route("/api/update_server")
def api_update_server():
    cur_time = datetime.now()

    for a in ANNOUNCEMENTS_LIST:
        if cur_time - a[3] > timedelta(7):
            ANNOUNCEMENTS_LIST.remove(a)
    
    return {"update_success": True}

@routes.route("/api/get_camera_feed")
def api_get_camera_feed():
    return get_camera_feed()

# ------------------------------------ DASHBOARD AND LOGIN ROUTES ---------------------------------
@routes.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home.html", name="")
    
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
            return render_template("dashboard.html", name=name, announcements=ANNOUNCEMENTS_LIST)
        
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))

# ------------------------------ FILES ROUTES ------------------------------------------------
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

                elif c == 'image':
                    path = dm.urlify(path, False)
                    return render_template(
                        "image_viewer.html", path=path, name=name
                    )
    
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
@routes.route("/<name>/get_file/<path>")
def get_file(name, path):
    if um.is_logged_in(name):
        return send_file(dm.urlify(path, False))
    
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
@routes.route("/<name>/delete/<path>/<p_type>", methods=['GET'])
def delete_file(name, path, p_type):
    if um.is_logged_in(name):
        if request.method == 'GET':
            path = dm.urlify(path, False)
            dm.delete_path(path, p_type)

            return redirect(url_for('routes.files', name=name, direc=dm.urlify(path.rsplit("/", 1)[0], True)))

    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))

# ------------------------------ CAMERAS ROUTES -------------------------------------
@routes.route("/<name>/cams")
def cams(name):
    if um.is_logged_in(name):
        return render_template("cams.html", name=name)
    
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))
    
# ------------------------------ ADDONS ROUTES --------------------------------------
@routes.route("/<name>/addons")
def addons(name):
    if um.is_logged_in(name):
        return render_template("addons.html", name=name, addons=cf["addons"])
    else:
        return redirect(url_for('routes.home', ERROR="Please log in"))

# ------------------------- ADMIN ROUTES -------------------------------------------
ADMIN_ROUTE_NAME = cf['server']['admin route']
@routes.route(f"/{ADMIN_ROUTE_NAME}/panel")
def admin_panel():
    if request.method == "GET":
        return render_template("admin_panel.html", administer='base')
    
@routes.route(f"/{ADMIN_ROUTE_NAME}/announce", methods=["GET", "POST"])
def admin_announce():
    if request.method == "GET":
        return render_template("admin_panel.html", administer='announce')
    
    else:
        announcement = request.form.get("announcement")
        level = int(request.form.get("announcement-level"))
        ANNOUNCEMENTS_LIST.append((announcement, level))
        return render_template("admin_panel.html", administer='base')