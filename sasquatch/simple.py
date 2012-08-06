#!/usr/bin/env python

import sys, os, shutil, json, subprocess, SimpleHTTPServer, SocketServer
from os import path

from util import *
from dev import DevBuild
from prod import ProdBuild

import time, re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


############################
##  Command Line Options
############################

def help():
    print '''
    usage sasquatch <cmd>

    Available commands:
    dev - provides a filewatch function to do partial compilations of simple projects
    dev server - same as dev but also provides a simple http server
    dev once - runs the dev build and then quits (does not continue watching)
    prod - build a production version of a simple project, minified using closure compiler
    create-project - create a new project folder structure
    create-view - add a new view and controller file to the current project

    Author - Todd Cullen todd@thoughtleadr.com, Nick Daugherty nick@thoughtleadr.com
    '''

def create_project():
    if len(sys.argv) > 2:
        os.mkdir(sys.argv[2])
        os.chdir(sys.argv[2])
    example_dir = script_dir("example")
    for f in os.listdir(example_dir):
        end_path = project_dir(append=f)
        start_path = os.path.join(example_dir, f)
        print f
        if not os.path.exists(end_path):
            print "start path: %s" % start_path
            if os.path.isdir(start_path):
                shutil.copytree(start_path, end_path)
            else:
                shutil.copy(start_path, end_path)

        else:
            print "skipped %s. already exists." % f


def update_framework():
    lib_dir = script_dir(append="example/lib")
    for f in os.listdir(lib_dir):
        end_path = project_dir(append="lib/%s" % f)
        start_path = os.path.join(lib_dir, f)
        if not os.path.exists(end_path):
            print "creating file >> %s" % start_path
        else:
            print "overwriting %s." % f

        if os.path.isdir(start_path):
            shutil.copytree(start_path, end_path)
        else:
            shutil.copy(start_path, end_path)

def create_view(name):

    if not os.path.exists(project_dir("view")):
        print "Not a valid simple project. Missing a 'view' folder."
        return

    if not os.path.exists(project_dir("controller")):
        print "Not a valid simple project. Missing a 'controller' folder."
        return

    js_src = """
exports.loadData = function(data, callback){
    console.log("view ready:%s");
    callback({});
};

exports.onReady = function(){
    console.log("view ready:%s");
};

exports.onFinished = function(){
    console.log("view exiting:%s");
};
    """ % (name, name, name)

    write_file(project_dir("view/%s.erb" % name), "")
    write_file(project_dir("controller/%s.js" % name), js_src)

def fetch_shared_dir():
    app_filename = project_dir(append="app.json")
    app_json = read_file(app_filename)
    app_conf = json.loads(app_json)
    if "shared_dir" in app_conf:
        return app_conf["shared_dir"]
    return None

def dev():
    # first time around do new build
    shared_dir = fetch_shared_dir()
    handler = DevBuild(project_dir(), script_dir(), shared_dir)
    handler.wrapped_all()

    observer = Observer()
    observer.schedule(handler, path=project_dir(), recursive=True)
    observer.start()

    if shared_dir is not None:
        observer = Observer()
        observer.schedule(handler, path=shared_dir, recursive=True)
        observer.start()

    if len(sys.argv) > 2 and sys.argv[2] == 'server':
        PORT = 8000
        server = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", PORT), server)
        print "serving at port", PORT
        try:
            while True:
                httpd.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            httpd.shutdown()
            observer.stop()

    if len(sys.argv) > 2 and sys.argv[2] == 'once':
        observer.stop()
    else:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

def server(httpd_old="None"):
    PORT = 8000
    server = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), server)
    print "serving at port", PORT
    httpd.serve_forever()
    return httpd

def debug():
    root_folders = [fetch_shared_dir(), project_dir()]
    folders = ["controller", "lib"]
    for root in root_folders:
        root = os.path.abspath(root)
        for folder in folders:
            # get every js file in that folder or subfolders and run debug on it
            base_folder = os.path.join(root, folder)
            if os.path.exists(base_folder):
                for f in os.listdir(base_folder):
                    if f.endswith(".js"):
                        compiler.debug(os.path.join(root, folder, f))


def prod():
    # first time around do new build
    handler = ProdBuild(project_dir(), script_dir(), fetch_shared_dir())
    handler.all(clean_proj=False)

def main():
    '''
    This is the awesome opt parser.
    '''
    length = len(sys.argv)
    if length == 3:
        arg = sys.argv[-1]
        cmd = sys.argv[-2]
    elif length == 2:
        cmd = sys.argv[-1]
    else:
        return help()

    if cmd == "create-project":
        return create_project()
    elif cmd == "update-framework":
        return update_framework()
    elif cmd == "clean":
        return _clean()
    elif cmd == "dev":
        return dev()
    elif cmd == "prod":
        return prod()
    elif cmd == "create-view":
        return create_view(arg)
    elif cmd == "debug":
        return debug()
    else:
        return help()


p = project_dir()
s = script_dir(append="templates")
template_dirs = [p, s]

from django.conf import settings
settings.configure(TEMPLATE_DIRS=template_dirs)


if __name__ == "__main__":
    with timer():
        main()


