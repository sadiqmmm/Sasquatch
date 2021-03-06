import sys, os, shutil, json, subprocess
from multiprocessing import Process, Array
from os import path

from util import *
from base import BaseBuild

import time, re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from django.template.loader import render_to_string


class DevBuild(BaseBuild):
    '''
    Dev Build System
    '''
    
    ################################
    #   Controller JS
    ################################
    
    def _prep_single_controller_js(self, folder, item, skip_controller=False):
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
        return result
        
    
    def __write_single_controller_js(self, folder, item, skip_controller=False):
        name = item.split(".")[0]
        result = self._prep_single_controller_js(folder, item, skip_controller)
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
        partial_dir = self.project_dir(append="partial")
        self.__write_controller_js(partial_dir, True)
        if self.has_shared():
            partial_dir = self.shared_dir("partial")
            self.__write_controller_js(partial_dir, True)
    
    ################################
    #   config.js
    ################################
    def prep_config_js(self):
        config_file = self.project_dir("config.json")
        config = read_file(config_file)
        try:
            json.loads(config)
        except Exception, e:
            raise Exception("Invalid JSON in the config.json. Please validate your configuration. file location => %s :: %s" % (config_file, e))
        result = "$.config = %s;" % config
        return result
        
    def write_config_js(self):
        print "writing config.js file to bin"
        result = self.prep_config_js()
        config_filename = self.bin_dir(append="scripts/config.js")
        write_file(config_filename, result)
    
    ################################
    #   JS Libraries
    ################################
    def flatten_name(self, filename):
        return re.sub("\/", "-", filename)
    
    def copy_dep_js(self, filename, basename=None):
        source = read_file(filename)
        if basename is None:
            basename = self.flatten_name(filename)
        else:
            basename = self.flatten_name(basename)
        script_name = self.bin_dir(append="scripts/%s" % basename)
        write_file(script_name, source)
    
    def load_app_json(self):
        app_filename = self.project_dir(append="app.json")
        app_json = read_file(app_filename)
        app_conf = json.loads(app_json)
        return app_conf
    
    def write_dep_js(self):
        print "writing core.js file to bin"
        app_conf = self.load_app_json()
        for item in app_conf["dependencies"]:
            if item.find("[shared]") == 0:
                basename = item[8:]
                self.copy_dep_js(self.shared_dir(basename), basename)
            else:
                self.copy_dep_js(self.project_dir(item), item)
        
    ################################
    #   HTML Template
    ################################
    
    def find_style_deps(self):
        styles = []
        for item in ["app.css"]:
            styles.append("styles/%s" % item)
        return styles
    
    def find_js_deps(self):
        app_filename = self.project_dir(append="app.json")
        app_json = read_file(app_filename)
        app_conf = json.loads(app_json)
        scripts = []
        for item in app_conf["dependencies"]:
            if item.find("[shared]") == 0:
                item = item[8:]
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
        return scripts
    
    def write_html(self):
        print "writing index.html to bin"
        scripts = self.find_js_deps()
        styles = self.find_style_deps()
        self.write_html_index(scripts, styles)
    
    def write_html_index(self, scripts, styles):
        result = render_to_string("template.html", {
            "scripts" : scripts,
            "styles" : styles,
            "ie_styles" : ["styles/ie.css"],
            "print_styles" : ["styles/print.css"]
        })
        index_filename = self.bin_dir(append="index.html")
        write_file(index_filename, result)
    
    ################################
    #   CSS & Images
    ################################
    
    def copy_standalone_sass(self):
        ie = self.project_dir("style/ie.scss")
        if os.path.exists(ie) or not self.has_shared():
            copy_file(ie, self.bin_dir("sass/ie.scss"))
        else:
            try:
                copy_file(self.shared_dir("style/ie.scss"), self.bin_dir("sass/ie.scss"))
            except:
                raise Exception("Missing the projects ie.scss file. It must be located in either the main project or the projects shared folder dir.")
            
        pri = self.project_dir("style/print.scss")
        if os.path.exists(pri) or not self.has_shared():
            copy_file(pri, self.bin_dir("sass/print.scss"))
        else:
            try:
                copy_file(self.shared_dir("style/print.scss"), self.bin_dir("sass/print.scss"))
            except:
                raise Exception("Missing the projects print.scss file. It must be located in either the main project or the projects shared folder dir.")
        
    
    def combine_app_sass(self):
        print "converting sass files to css and writing to bin"
        app_json = self.load_app_json()
        sass_src = ""
        for filename in app_json["app_sass"]:
            if self.has_shared() and filename.find("[shared]") == 0:
                filename = self.shared_dir(filename[8:])
            sass_src += "\n/*\nfile: %s\n*/\n" % filename
            sass_src += read_file(filename)
        write_file(self.bin_dir("sass/app.scss"), sass_src)

    def run_compass(self):
        external_process("compass", "compile", self.bin_dir())
    
    ################################
    #   Images
    ################################
    
    def write_sprites(self):
        return
        print "generating spritesheet awesomeness..."
        start_folder = self.project_dir("sprites")
        sass_folder = self.bin_dir("sass")
        img_folder = self.bin_dir("img")
        
        external_process("glue", start_folder, "--img=%s" % img_folder, "--css=%s" % sass_folder, "--simple", "--crop")
        
        orig = read_file(self.bin_dir("sass/_app.scss"))
        
        if(os.path.exists(self.bin_dir("sass/sprites.scss"))):
            add_on = read_file(self.bin_dir("sass/sprites.scss"))
            write_file(self.bin_dir("sass/app.scss"), add_on + orig)
            os.remove(self.bin_dir("sass/_app.scss"))
            os.remove(self.bin_dir("sass/sprites.scss"))
        else:
            write_file(self.bin_dir("sass/app.scss"), orig)
            os.remove(self.bin_dir("sass/_app.scss"))
        
    
    def copy_img(self):
        end_path = self.bin_dir(append="img")
        if self.has_shared():
            start_path = self.shared_dir("img")
            if os.path.exists(start_path):
                copytree(start_path, end_path)
        
        start_path = self.project_dir(append="img")
        copytree(start_path, end_path)
    
    ################################
    #   Routes
    ################################
    
    def prep_routes_js(self):
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
        return result
    
    def write_routes(self):
        print "writing routes to bin"
        result = self.prep_routes_js()
        route_filename = self.bin_dir(append="scripts/routes.js")
        write_file(route_filename, result)
    
    ############################
    ##  Dev Event Handling
    ############################
    
    def all(self, clean_proj=True):
        if clean_proj:
            self.clean()
        with timer("write_config_js"):
            self.write_config_js()
        
        with timer("write_routes"):
            self.write_routes()
        
        with timer("write_controller_js"):
            self.write_controller_js()
        
        with timer("write_dep_js"):
            self.write_dep_js()
        
        #generate sprites
        with timer("copy_img"):
            self.copy_img()
        
        #sass compilation
        with timer("copy_standalone_sass"):
            self.copy_standalone_sass()
        
        with timer("combine_app_sass"):
            self.combine_app_sass()
        
        with timer("write_sprites"):
            self.write_sprites()
        
        with timer("run_compass"):
            self.run_compass()
        
        with timer("write_html"):
            self.write_html()
    
    def partial(self, event):
        src_path = event.src_path
        basename = path.basename(src_path)
        if event.is_directory or basename.startswith("."):
            print "no action"
            return
        
        # Shared dir actions first
        if self.has_shared():
            if src_path.startswith(self.shared_dir("styles")):
                print "partial sass."
                if src_path.endswith("ie.scss") or src_path.endswith("print.scss"):
                    self.copy_standalone_sass()
                else:
                    self.combine_app_sass()
                    self.write_sprites()
                return self.run_compass()
            elif src_path.startswith(self.shared_dir(append="partial")):
                print "rewrite all controllers - shared"
                return self.write_controller_js()
            elif src_path.startswith(self.shared_dir(append="lib")):
                sub_path = src_path.replace(self.shared_dir()+"/", "")
                print "copy dependency -> %s" % sub_path
                return self.copy_dep_js(src_path, sub_path)
            elif src_path.startswith(self.shared_dir(append="img")):
                print "copy images"
                return self.copy_img()
        
        # Standard Simple project partial actions
        if src_path.startswith(self.project_dir("style")):
            print "partial sass."
            if src_path.endswith("ie.scss") or src_path.endswith("print.scss"):
                self.copy_standalone_sass()
            else:
                self.combine_app_sass()
                self.write_sprites()
            self.run_compass()
        elif src_path == self.project_dir(append="template.html"):
            print "template rewrite"
            self.write_html()
        elif src_path == self.project_dir(append="config.json"):
            print "config rewrite"
            self.write_config_js()
        elif src_path.startswith(self.project_dir(append="controller")) and basename.endswith(".js"):
            print "single controller rewrite"
            self.__write_single_controller_js(self.project_dir("view"), basename)
        elif src_path.startswith(self.project_dir(append="view")):
            print "rewrite all controllers"
            self.write_controller_js()
        elif src_path.startswith(self.project_dir(append="partial")):
            print "rewrite all controllers - shared"
            self.write_controller_js()
        elif src_path == self.project_dir(append="app.json"):
            print "rewrite all deps"
            self.write_dep_js()
        elif src_path.startswith(self.project_dir(append="lib")):
            sub_path = src_path.replace(self.project_dir()+"/", "")
            print "copy dependency -> %s" % sub_path
            self.copy_dep_js(src_path, sub_path)
        elif src_path.startswith(self.project_dir(append="sprites")):
            print "rewrite sprites"
            self.combine_app_sass()
            self.write_sprites()
            self.run_compass()
        elif src_path.startswith(self.project_dir(append="routes.json")):
            print "rewrite routes"
            self.write_routes()
        elif src_path.startswith(self.project_dir(append="img")):
            print "copy images"
            self.copy_img()
        else:
            print "no action*"
        
    
    



