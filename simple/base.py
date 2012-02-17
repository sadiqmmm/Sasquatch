from util import *
import sys, os, shutil, json, subprocess
from watchdog.events import FileSystemEventHandler

class BaseBuild(FileSystemEventHandler):
    
    def __init__(self, project_dir, script_dir):
        self.__project = project_dir
        self.__script = script_dir
        self.__bin = "%s/bin" % self.__project
    
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
    
    def clean(self):
        if os.path.exists(self.bin_dir()):
            shutil.rmtree(self.bin_dir())
        os.mkdir("bin")
        os.mkdir("bin/scripts")
        os.mkdir("bin/styles")
    
    def skip_bin(self, path):
        if path.find(self.bin_dir()) > -1:
            return True
        return False
    
    
    
    def all(self, event):
        pass
    
    def partial(self, event):
        pass
    
    def wrapped_partial(self, event):
        if not self.skip_bin(event.src_path):
            try:
                self.partial(event)
            except Exception, e:
                print "## Exception during a partial recompile ##"
                print "Error => %s" % str(e)
        
        
    
    def on_moved(self, event):
        super(BaseBuild, self).on_moved(event)
        
        what = 'directory' if event.is_directory else 'file'
        print "Moved %s: from %s to %s" % (what, event.src_path, event.dest_path)
        
        if not self.skip_bin(event.src_path):
            self.all(event)
    
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
            self.all(event)
        
    
    def on_modified(self, event):
        super(BaseBuild, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        print "Modified %s: %s" % (what, event.src_path)
        self.wrapped_partial(event)
    
