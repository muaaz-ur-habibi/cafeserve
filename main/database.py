from __future__ import annotations
from os.path import dirname, isdir
from os import makedirs, listdir, remove
from shutil import rmtree
from subprocess import Popen, PIPE
from base64 import urlsafe_b64decode, urlsafe_b64encode
import mimetypes

from pprint import pp

mimetypes.add_type("video/mp2t", ".ts")

class FileNode:
    def __init__(self, parent:FileNode, name:str, child:list[FileNode], is_file:bool=False):
        self.parent = parent
        self.name = name
        self.child = child
        self.is_file = is_file

        if not is_file:
            self.type = 'folder'
        else:
            self.type = 'file'

class DatabaseManager:
    def __init__(self, base_dir:str):
        if not isdir(base_dir):
            makedirs(base_dir, exist_ok=True)
            makedirs(f"{base_dir}/Media", exist_ok=True)
            makedirs(f"{base_dir}/Scripts", exist_ok=True)
            makedirs(f"{base_dir}/Documents", exist_ok=True)

        self.BASE_DIR = base_dir
        self.CUR_DIR = self.BASE_DIR
        self.ROOT_NODE = FileNode(None, self.BASE_DIR, [])
        self.CUR_NODE = self.ROOT_NODE

        self.running_processes = {'job_id': 'Process'}

    # AI function
    def print_tree(self, node: FileNode = None, indent: str = "", is_last: bool = True):
        if node is None:
            node = self.ROOT_NODE      # start at root

        connector = "└── " if is_last else "├── "

        # Print the current node
        if node == self.ROOT_NODE:
            print(f"{node.name}/")  # root
        else:
            print(indent + connector + node.name + ("/" if node.child else ""))

        # Prepare indentation for children
        new_indent = indent + ("    " if is_last else "│   ")

        # Recurse into children
        for i, child in enumerate(node.child):
            last = (i == len(node.child) - 1)
            self.print_tree(child, new_indent, last)


    def rebuild_nodes(self, node: FileNode, path: str = None):
        if path is None:
            path = self.BASE_DIR

        node.child = []

        for name in listdir(path):
            full_path = f"{path}/{name}"

            # recurse only if this is a directory
            if isdir(full_path):
                # folder
                child = FileNode(node, name, [], False)
                child = self.rebuild_nodes(child, full_path)
                node.child.append(child)
            else:
                # file
                child = FileNode(node, name, [], True)
                node.child.append(child)

        return node
    
    def add_node(self, name:str, dir:str, is_file:bool):
        self.CUR_NODE = self.get_node_from_path(dir)
        self.CUR_NODE.child.append(
            FileNode
            (
                self.CUR_NODE, name, [], is_file
            )
        )

    def add_path(self, path:str, is_file_path:bool, file_contents:bytes=None):
        if not is_file_path:
            makedirs(path, exist_ok=True)
        else:
            makedirs(dirname(path), exist_ok=True)

            with open(path, "wb") as f:
                f.write(file_contents)

    def get_node_from_path(self, path:str):
        path = path.split(self.BASE_DIR)[-1].replace("\\", "/").split("/")

        node = self.ROOT_NODE
        for p in path:
            for child in node.child:
                if child.name == p:
                    node = child
                    break
    
        return node
    
    def get_path_from_node(self, node:FileNode):
        path = ""

        n = node
        while n != self.ROOT_NODE:
            path += n.name
            n = n.parent

        return path

    def get_file_contents(self, path:str):
        c = ""
        with open(path, "rb") as f:
            try:
                c = f.read().decode().strip()

                if c == '':
                    c = f"UG_{mimetypes.guess_type(path)[0]}"
            
            except UnicodeDecodeError:
                c = f"UG_{mimetypes.guess_type(path)[0]}"
                print("Guessed", c)
            
        return c

    def get_database_list(self, node:FileNode=None):
        l:dict = {}
            
        for child in node.child:
            if child.child != []:
                l[child.name] = self.get_database_list(child)
                l[child.name]['type'] = child.type
            
            else:
                l[child.name] = {
                    'type': child.type
                }

        l = {node.name: l, 'type': node.type}

        return l
    
    def get_current_path_list(self, db_list:dict):
        paths = self.CUR_DIR.split(self.BASE_DIR)
        non_root = paths.pop(-1)
        non_root = non_root.split("/")

    def urlify(self, path:str, to_url:bool):
        if to_url:
            return urlsafe_b64encode(path.encode()).decode()
        else:
            return urlsafe_b64decode(path.encode()).decode()
        
    def delete_path(self, path, p_type):
        if p_type == 'file':
            remove(path)

        elif p_type == 'folder':
            rmtree(path, ignore_errors=True)