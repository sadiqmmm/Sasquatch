#!/usr/bin/env python

import sys, os, shutil, json, subprocess
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
    usage simple <cmd>
    
    Available commands:
    dev - provides a filewatch function to do partial compilations of simple projects
    prod - build a production version of a simple project
    create-project - create a new project folder structure
    create-view - add a new view and controller file to the current project
    
    Author - Todd Cullen todd@thoughtleadr.com
    '''

def create_project():
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
    return None

def dev():
    # first time around do new build
    shared_dir = fetch_shared_dir()
    handler = DevBuild(project_dir(), script_dir(), shared_dir)
    handler.all()
    
    observer = Observer()
    observer.schedule(handler, path=project_dir(), recursive=True)
    observer.start()
    
    observer = Observer()
    observer.schedule(handler, path=shared_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

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
        create_view(arg)
    else:
        return help()
    

p = project_dir()
s = script_dir(append="templates")
template_dirs = [p, s]

from django.conf import settings
settings.configure(TEMPLATE_DIRS=template_dirs)


if __name__ == "__main__":
    main()


