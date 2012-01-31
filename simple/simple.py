#!/usr/bin/env python

import sys, os, shutil, json, codecs, subprocess
from os import path

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def read_file(location):
    f = codecs.open(location, encoding='utf-8', mode="rb")
    result = f.read()
    f.close()
    return result

def write_file(location, txt):
    f = codecs.open(location, encoding='utf-8', mode="wb")
    f.write(txt)
    f.close()

##############
#  Dev 
##############
def write_controller_js():
    print "Writing controller.js file to bin"
    views = []
    for item in os.listdir(project_dir(append="view")):
        # make sure we don't iterate over a .DS_Store or something irrelevant
        if item.endswith(".erb") and not item.startswith("."):
            name = item.split(".")[0]
            view = read_file(project_dir(append="view/%s.erb" % name))
            controller = read_file(project_dir(append="controller/%s.js" % name))
            views.append({
                "name" : name,
                "template" : view,
                "controller" : controller
            })
        
    for item in os.listdir(project_dir(append="partial")):
        if item.endswith("erb") and not item.startswith("."):
            name = item.split(".")[0]
            view = read_file(project_dir(append="partial/%s.erb" % name))
            views.append({
                "name" : name,
                "template" : view,
                "controller" : ""
            })
        
    result = render_to_string("controller.js", {
        "views" : views,
    })
    write_file(bin_dir(append="controller.js"), result)

def write_config_js():
    print "writing config.js file to bin"
    config = read_file(project_dir("config.json"))
    try:
        json.loads(config)
    except:
        raise Exception("Invalid JSON in the config.json. Please validate your configuration.")
    result = "$.config = %s" % config
    write_file(bin_dir(append="config.js"), result)

def write_dep_js():
    print "writing core.js file to bin"
    app_json = read_file(project_dir(append="app.json"))
    app_conf = json.loads(app_json)
    source = u""
    for item in app_conf["dependencies"]:
        source += u"\n//******************\n//  file:%s\n//******************\n" % item
        a = read_file(project_dir(append=item))
        source += a
    write_file(bin_dir(append="core.js"), source)

def write_html():
    print "writing index.html to bin"
    result = render_to_string("template.html", {
        "scripts" : ["core.js", "config.js", "controller.js"]
    })
    write_file(bin_dir(append="index.html"), result)

def write_all_sass():
    print "converting sass files to css and writing to bin"
    for filename in os.listdir(project_dir(append="style")):
        if filename.endswith("scss") and not filename.startswith("."):
            write_sass(filename)

def write_sass(filename):
    filename = filename.replace(".scss", "")
    print "writing %s.css to bin" % filename
    scss_file = project_dir(append="style/%s.scss" % filename)
    css_file = project_dir(append="bin/%s.css" % filename)
    result = subprocess.call(["sass", scss_file, css_file])
    if result > 0:
        raise Exception("Error processing SASS file >> %s -> %s" % (scss_file, css_file))
    

##############
#  File References 
##############

def project_dir(append=None):
    base = os.getcwd()
    if append is not None:
        return os.path.join(base, append)
    return base
    

def bin_dir(append=None):
    base = project_dir(append="bin")
    if append is not None:
        return os.path.join(base, append)
    return base

def script_dir(append=None):
    file_location = None
    try:
        file_location = os.path.dirname(__file__)
    except:
        file_location = "./"
    
    if append is not None:
        return os.path.join(file_location, append)
    return file_location

##############
#  Utility Methods 
##############

def _clean():
    if os.path.exists(bin_dir()):
        shutil.rmtree(bin_dir())
    os.mkdir("bin")

def clean(f):
    def inner():
        _clean()
        f()
    return inner

##############
#  Command Line Options
##############

def help():
    print '''
    You should probably mention that I need to get filled out.
    Email todd@thoughtleadr.com and tell him to get on it!
    '''

@clean
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
        

def skip_bin(f):
    '''
    TODO: Make this more generic
    '''
    def inner(self, event):
        if event.src_path.find("/bin") > -1:
            return
        return f(self, event)
    return inner

class DevEventHandler(FileSystemEventHandler):
    """
    When a file system event occurs, trigger a new build.
    TODO: Make the build system more efficient, currently always does a full rebuild.
    """
    
    def all(self, clean_proj=True):
        if clean_proj:
            _clean()
        write_config_js()
        write_controller_js()
        write_dep_js()
        write_all_sass()
        write_html()
    
    def partial(self, event):
        if event.is_directory or path.basename(event.src_path).startswith("."):
            return
        
        style_path = project_dir(append="style")
        if event.src_path.startswith(style_path):
            filename = event.src_path.replace(style_path, "")
            return write_scss(filename)
        elif event.src_path == project_dir(append="template.html"):
            write_html()
        elif event.src_path == project_dir(append="config.json"):
            write_config()
        elif event.src_path.startswith(project_dir(append="controller")) and event.src_path.endswith(".js"):
            write_controller_js()
        elif event.src_path == project_dir(append="app.json"):
            write_dep_js()
        
    
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
        
        

@clean
def dev():
    # first time around do new build
    handler = DevEventHandler()
    handler.all(clean_proj=False)
    
    observer = Observer()
    observer.schedule(handler, path=project_dir(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@clean
def prod():
    pass

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
    elif cmd == "clean":
        return _clean()
    elif cmd == "dev":
        return dev()
    elif cmd == "prod":
        return prod()
    else:
        return help()
    


from django.conf import settings
settings.configure(TEMPLATE_DIRS=[project_dir(), script_dir(append="templates")])

from django.template.loader import render_to_string


if __name__ == "__main__":
    main()


