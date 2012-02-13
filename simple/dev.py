import sys, os, shutil, json, subprocess
from os import path

from util import *

import time, re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from django.conf import settings
settings.configure(TEMPLATE_DIRS=[project_dir(), script_dir(append="templates")])

from django.template.loader import render_to_string


###########################
#
#   Dev Build System
#
###########################

def skip_bin(f):
    '''
    TODO: Make this more generic
    '''
    def inner(self, event):
        if event.src_path.find("/bin") > -1:
            return
        return f(self, event)
    return inner


class DevBuild(FileSystemEventHandler):
    def __init__(self, project_dir, script_dir):
        self.__project = project_dir
        self.__script = script_dir
    
    #######################
    #   File Utils
    #######################
    def project_dir(self, append=None):
        if append is not None:
            return "%s%s" % (self.__project, append)
        return self.__project
    
    def script_dir(self, append=None):
        if append is not None:
            return "%s%s" % (self.__script, append)
        return self.__script
    
    def bin_dir(self, append=None):
        if append is not None:
            return "%s%s" % (self.__project, append)
        return self.__project
    
    #######################
    #   Dev Build Steps
    #######################
    
    def __write_controller_js(self, folder, skip_controller=False):
        for item in os.listdir(folder):
            # make sure we don't iterate over a .DS_Store or something irrelevant
            if item.endswith(".erb") and not item.startswith("."):
                name = item.split(".")[0]
                view = read_file("%s/%s.erb" % (folder, name))
                if not skip_controller:
                    controller = read_file(project_dir(append="controller/%s.js" % name))
                else:
                    controller = ""
                views = []
                views.append({
                    "name" : name,
                    "template" : view,
                    "controller" : controller
                })
                result = render_to_string("controller.js", {
                    "views" : views,
                })
                write_file(bin_dir(append="scripts/%s.js" % name), result)
    

    def write_controller_js(self):
        print "Writing controller.js file to bin"
        __write_controller_js(project_dir(append="view"))
        __write_controller_js(project_dir(append="partial"), True)


    def write_config_js(self):
        print "writing config.js file to bin"
        config_file = project_dir("config.json")
        config = read_file(config_file)
        try:
            json.loads(config)
        except Exception, e:
            raise Exception("Invalid JSON in the config.json. Please validate your configuration. file location => %s :: %s" % (config_file, e))
        result = "$.config = %s" % config
        write_file(bin_dir(append="scripts/config.js"), result)

    def flatten_name(self, filename):
        return re.sub("\/", "-", filename)

    def write_dep_js(self):
        print "writing core.js file to bin"
        app_json = read_file(project_dir(append="app.json"))
        app_conf = json.loads(app_json)
        for item in app_conf["dependencies"]:
            filename = project_dir(append=item)
            source = read_file(filename)
            basename = flatten_name(item)
            write_file(bin_dir(append="scripts/%s" % basename), source)
    

    def write_html(self):
        print "writing index.html to bin"
    
        app_json = read_file(project_dir(append="app.json"))
        app_conf = json.loads(app_json)
        scripts = []
        for item in app_conf["dependencies"]:
            basename = flatten_name(item)
            scripts.append("scripts/%s" % basename)
    
        # iterate over files and subfiles in bin for css and scripts
        scripts.append("scripts/config.js")
        scripts.append("scripts/routes.js")
        for item in os.listdir(bin_dir(append="scripts")):
            loc = "scripts/%s" % item
            if loc not in scripts:
                scripts.append(loc)
        
        styles = []
        for item in os.listdir(bin_dir(append="styles")):
            styles.append("styles/%s" % item)
        
    
        result = render_to_string("template.html", {
            "scripts" : scripts,
            "styles" : styles
        })
        write_file(bin_dir(append="index.html"), result)

    def write_all_sass(self):
        print "converting sass files to css and writing to bin"
        for filename in os.listdir(project_dir(append="style")):
            if filename.endswith("scss") and not filename.startswith("."):
                write_sass(filename)

    def write_sass(self, filename):
        filename = filename.replace(".scss", "")
        print "writing %s.css to bin" % filename
        scss_file = project_dir(append="style/%s.scss" % filename)
        css_file = bin_dir(append="styles/%s.css" % filename)
        result = subprocess.call(["sass", scss_file, css_file])
        if result > 0:
            raise Exception("Error processing SASS file >> %s -> %s" % (scss_file, css_file))
    
    def write_sprites(self):
        print "generating spritesheet awesomeness..."
        start_folder = project_dir(append="sprites")
        dest_folder = bin_dir(append="styles")
        result = subprocess.call(["glue", start_folder, dest_folder, "--simple"])
        if result > 0:
            raise Exception("Error generating spritesheet")
    

    def write_routes(self):
        print "writing routes to bin"
        routes = read_file(project_dir("routes.json"))
        try:
            routes = json.loads(routes)
        except:
            raise Exception("Invalid JSON in the routes.json. Please validate your configuration.")
    
        r = []
        for name in routes:
            o = routes[name]
            o["pattern"] = name
            r.append(o)
    
        result = render_to_string("routes.js", { "routes" : r })
        write_file(bin_dir(append="scripts/routes.js"), result)

    def copy_img(self):
        start_path = project_dir(append="img")
        end_path = bin_dir(append="img")
        shutil.copytree(start_path, end_path)
    
    ############################
    ##  Dev Event Handling
    ############################
    
    def all(self, clean_proj=True):
        if clean_proj:
            _clean()
        write_config_js()
        write_routes()
        write_controller_js()
        write_dep_js()
        write_all_sass()
        write_sprites()
        copy_img()
        write_html()
    
    def partial(self, event):
        src_path = event.src_path
        basename = path.basename(src_path)
        if event.is_directory or basename.startswith("."):
            return
        
        if src_path.startswith(project_dir(append="style")):
            write_sass(basename)
        elif src_path == project_dir(append="template.html"):
            write_html()
        elif src_path == project_dir(append="config.json"):
            write_config()
        elif src_path.startswith(project_dir(append="controller")) and basename.endswith(".js"):
            write_controller_js()
        elif src_path.startswith(project_dir(append="view")):
            write_controller_js()
        elif src_path == project_dir(append="app.json") or src_path.startswith(project_dir(append="lib")):
            write_dep_js()
        elif src_path.startswith(project_dir(append="sprites")):
            write_sprites()
        elif src_path.startswith(project_dir(append="routes.json")):
            write_routes()
        elif src_path.startswith(project_dir(append="img")):
            copy_img()
        
    
    @skip_bin
    def on_moved(self, event):
        super(DevEventHandler, self).on_moved(event)
        
        what = 'directory' if event.is_directory else 'file'
        print "Moved %s: from %s to %s" % (what, event.src_path, event.dest_path)
        self.all()
    
    @skip_bin
    def on_created(self, event):
        super(DevEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        print "Created %s: %s" % (what, event.src_path)
        self.partial(event)
    
    @skip_bin
    def on_deleted(self, event):
        super(DevEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        print "Deleted %s: %s" % (what, event.src_path)
        self.all()
    
    @skip_bin
    def on_modified(self, event):
        super(DevEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        print "Modified %s: %s" % (what, event.src_path)
        self.partial(event)
    



