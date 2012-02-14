import sys, os, shutil, json, subprocess
from os import path

from util import *
from base import BaseBuild

import time, re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from django.conf import settings
settings.configure(TEMPLATE_DIRS=[project_dir(), script_dir(append="templates")])

from django.template.loader import render_to_string


class DevBuild(BaseBuild):
    '''
    Dev Build System
    '''
    
    def __write_single_controller_js(self, folder, item, skip_controller=False):
        print "FOLDER >> %s" % folder
        print "ITEM >> %s" % item
        name = item.split(".")[0]
        view = read_file("%s/%s.erb" % (folder, name))
        if not skip_controller:
            controller_filename = self.project_dir(append="controller/%s.js" % name)
            controller = read_file(controller_filename)
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
        out_filename = self.bin_dir(append="scripts/%s.js" % name)
        write_file(out_filename, result)
        
    
    def __write_controller_js(self, folder, skip_controller=False):
        for item in os.listdir(folder):
            # make sure we don't iterate over a .DS_Store or something irrelevant
            if item.endswith(".erb") and not item.startswith("."):
                self.__write_single_controller_js(folder, item, skip_controller)
        

    def write_controller_js(self):
        print "Writing controller.js file to bin"
        view_dir = self.project_dir(append="view")
        self.__write_controller_js(view_dir)
        partial_dir = project_dir(append="partial")
        self.__write_controller_js(partial_dir, True)
    
    def write_config_js(self):
        print "writing config.js file to bin"
        config_file = self.project_dir("config.json")
        config = read_file(config_file)
        try:
            json.loads(config)
        except Exception, e:
            raise Exception("Invalid JSON in the config.json. Please validate your configuration. file location => %s :: %s" % (config_file, e))
        result = "$.config = %s;" % config
        config_filename = self.bin_dir(append="scripts/config.js")
        write_file(config_filename, result)

    def flatten_name(self, filename):
        return re.sub("\/", "-", filename)
    
    def copy_dep_js(self, item):
        filename = self.project_dir(append=item)
        source = read_file(filename)
        basename = self.flatten_name(item)
        script_name = self.bin_dir(append="scripts/%s" % basename)
        write_file(script_name, source)
    
    def write_dep_js(self):
        print "writing core.js file to bin"
        app_filename = self.project_dir(append="app.json")
        app_json = read_file(app_filename)
        app_conf = json.loads(app_json)
        for item in app_conf["dependencies"]:
            self.copy_dep_js(item)
        
    
    def write_html(self):
        print "writing index.html to bin"
        app_filename = self.project_dir(append="app.json")
        app_json = read_file(app_filename)
        app_conf = json.loads(app_json)
        scripts = []
        for item in app_conf["dependencies"]:
            basename = self.flatten_name(item)
            scripts.append("scripts/%s" % basename)
    
        # iterate over files and subfiles in bin for css and scripts
        scripts.append("scripts/config.js")
        scripts.append("scripts/routes.js")
        script_dir = self.bin_dir(append="scripts")
        for item in os.listdir(script_dir):
            loc = "scripts/%s" % item
            if loc not in scripts:
                scripts.append(loc)
        
        styles = []
        styles_dir = self.bin_dir(append="styles")
        for item in os.listdir(styles_dir):
            styles.append("styles/%s" % item)
    
        result = render_to_string("template.html", {
            "scripts" : scripts,
            "styles" : styles
        })
        index_filename = self.bin_dir(append="index.html")
        write_file(index_filename, result)

    def write_all_sass(self):
        print "converting sass files to css and writing to bin"
        style_dir = self.project_dir(append="style")
        for filename in os.listdir(style_dir):
            if filename.endswith("scss") and not filename.startswith("."):
                self.write_sass(filename)

    def write_sass(self, filename):
        filename = filename.replace(".scss", "")
        print "writing %s.css to bin" % filename
        
        scss_file = self.project_dir(append="style/%s.scss" % filename)
        css_file = self.bin_dir(append="styles/%s.css" % filename)
        result = subprocess.call(["sass", scss_file, css_file])
        if result > 0:
            raise Exception("Error processing SASS file >> %s -> %s" % (scss_file, css_file))
    
    def write_sprites(self):
        print "generating spritesheet awesomeness..."
        start_folder = self.project_dir(append="sprites")
        dest_folder = self.bin_dir(append="styles")
        result = subprocess.call(["glue", start_folder, dest_folder, "--simple"])
        if result > 0:
            raise Exception("Error generating spritesheet")
    

    def write_routes(self):
        print "writing routes to bin"
        route_filename = self.project_dir("routes.json")
        routes = read_file(route_filename)
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
        route_filename = self.bin_dir(append="scripts/routes.js")
        write_file(route_filename, result)

    def copy_img(self):
        start_path = self.project_dir(append="img")
        end_path = self.bin_dir(append="img")
        shutil.copytree(start_path, end_path)
    
    ############################
    ##  Dev Event Handling
    ############################
    
    def all(self, clean_proj=True):
        if clean_proj:
            _clean()
        self.write_config_js()
        self.write_routes()
        self.write_controller_js()
        self.write_dep_js()
        self.write_all_sass()
        self.write_sprites()
        self.copy_img()
        self.write_html()
    
    def partial(self, event):
        src_path = event.src_path
        basename = path.basename(src_path)
        if event.is_directory or basename.startswith("."):
            return
        
        if src_path.startswith(self.project_dir(append="style")):
            self.write_sass(basename)
        elif src_path == self.project_dir(append="template.html"):
            self.write_html()
        elif src_path == self.project_dir(append="config.json"):
            self.write_config_js()
        elif src_path.startswith(self.project_dir(append="controller")) and basename.endswith(".js"):
            self.__write_single_controller_js(self.project_dir("view"), basename)
        elif src_path.startswith(self.project_dir(append="view")):
            self.write_controller_js()
        elif src_path == self.project_dir(append="app.json"):
            self.write_dep_js()
        elif src_path.startswith(self.project_dir(append="lib")):
            sub_path = src_path.replace(self.project_dir()+"/", "")
            self.copy_dep_js(sub_path)
        elif src_path.startswith(self.project_dir(append="sprites")):
            self.write_sprites()
        elif src_path.startswith(self.project_dir(append="routes.json")):
            self.write_routes()
        elif src_path.startswith(self.project_dir(append="img")):
            self.copy_img()
        
    
    



