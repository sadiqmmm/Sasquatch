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
    You should probably mention that I need to get filled out.
    Email todd@thoughtleadr.com and tell him to get on it!
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
        
      

def dev():
    # first time around do new build
    handler = DevBuild(project_dir(), script_dir())
    handler.all()
    
    observer = Observer()
    observer.schedule(handler, path=project_dir(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def prod():
    # first time around do new build
    handler = ProdBuild(project_dir(), script_dir())
    handler.all(clean_proj=False)

def main():
    '''
    This is the awesome opt parser.
    '''
    if len(sys.argv) > 2:
        return help()
    
    cmd = sys.argv[-1]
    print "CMD >> %s" % cmd
    
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
    else:
        return help()
    

p = project_dir()
s = script_dir(append="templates")
template_dirs = [p, s]
print "TEMPLATE_DIRS %s" % template_dirs

from django.conf import settings
settings.configure(TEMPLATE_DIRS=template_dirs)


if __name__ == "__main__":
    main()


