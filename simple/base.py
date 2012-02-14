
from watchdog.events import FileSystemEventHandler



class BaseBuild(FileSystemEventHandler):
    
    def __init__(self, project_dir, script_dir):
        self.__project = project_dir
        self.__script = script_dir
    
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
            return "%s/bin/%s" % (self.__project, append)
        return self.__project
    
    def clean(self):
        if os.path.exists(self.bin_dir()):
            shutil.rmtree(self.bin_dir())
        os.mkdir(self.project_dir(append="bin"))
        os.mkdir(self.project_dir(append="bin/scripts"))
        os.mkdir(self.project_dir(append="bin/styles"))
    
    def skip_bin(self, path):
        if path.find(self.bin_dir()) > -1:
            return False
        return True
    
    
    
    def all(self, event):
        pass
    
    def partial(self, event):
        pass
    
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
        
        if not self.skip_bin(event.src_path):
            self.partial(event)
        
    
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
        if not self.skip_bin(event.src_path):
            self.partial(event)
        
    
