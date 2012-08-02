from util import *
import sys, os, shutil, json, subprocess
from watchdog.events import FileSystemEventHandler

class BaseBuild(FileSystemEventHandler):
    
    def __init__(self, project_dir, script_dir, shared_dir):
        self.__project = project_dir
        self.__script = script_dir
        self.__bin = "%s/bin" % self.__project
        if shared_dir is None:
            self.__has_shared_dir = False
        else:
            self.__has_shared_dir = True
            self.__shared_dir = os.path.abspath(shared_dir)
        
    
    #######################
    #   File Utils
    #######################
    def project_dir(self, append=None):
        if append is not None:
            return "%s/%s" % (self.__project, append)
        return self.__project
    
    def script_dir(self, append=None):
        if append is not None:
            return "%s/%s" % (self.__script, append)
        return self.__script
    
    def bin_dir(self, append=None):
        if append is not None:
            return "%s/%s" % (self.__bin, append)
        return self.__bin
    
    def has_shared(self):
        return self.__has_shared_dir
    
    def shared_dir(self, append=None):
        if append is not None:
            return "%s/%s" % (self.__shared_dir, append)
        return self.__shared_dir
    
    def clean(self):
        if os.path.exists(self.bin_dir()):
            shutil.rmtree(self.bin_dir())
        os.mkdir("bin")
        os.mkdir("bin/scripts")
        os.mkdir("bin/styles")
        os.mkdir("bin/sass")
        self.write_compass_config()
        
    
    def write_compass_config(self):
        config_rb = '''
http_path = "/"
css_dir = "styles"
sass_dir = "sass"
images_dir = "img"
javascripts_dir = "scripts"
        '''
        
        write_file(self.bin_dir("config.rb"), config_rb)
    
    def skip_bin(self, path):
        if path.find(self.bin_dir()) > -1:
            return True
        return False
    
    def all(self):
        pass
    
    def partial(self, event):
        pass
    
    def wrapped_partial(self, event):
        if not self.skip_bin(event.src_path):
            try:
                with timer("partial"):
                    self.partial(event)
            except Exception, e:
                print "## Exception during a partial recompile ##"
                print "Error => %s" % str(e)
        
    def wrapped_all(self):
        with timer("all"):
            self.all()
    
    def on_moved(self, event):
        super(BaseBuild, self).on_moved(event)
        
        what = 'directory' if event.is_directory else 'file'
        print "Moved %s: from %s to %s" % (what, event.src_path, event.dest_path)
        
        if not self.skip_bin(event.src_path):
            self.wrapped_all()
    
    def on_created(self, event):
        super(BaseBuild, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        print "Created %s: %s" % (what, event.src_path)
        
        self.wrapped_partial(event)
    
    def on_deleted(self, event):
        super(BaseBuild, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        print "Deleted %s: %s" % (what, event.src_path)
        
        if not self.skip_bin(event.src_path):
            self.wrapped_all()
        
    
    def on_modified(self, event):
        super(BaseBuild, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        print "Modified %s: %s" % (what, event.src_path)
        self.wrapped_partial(event)
    
