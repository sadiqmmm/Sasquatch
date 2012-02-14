from dev import DevBuild
from util import *

class ProdBuild(DevBuild):
    
    def __prep_controller_js(self, folder, skip_controller=False):
        source = u""
        for item in os.listdir(folder):
            # make sure we don't iterate over a .DS_Store or something irrelevant
            if item.endswith(".erb") and not item.startswith("."):
                source += self._prep_single_controller_js(folder, item, skip_controller)
        return source

    def prep_controller_js(self):
        print "Create controller string"
        view_dir = self.project_dir(append="view")
        source = self.__prep_controller_js(view_dir)
        partial_dir = project_dir(append="partial")
        source += self.__prep_controller_js(partial_dir, True)
        
        return source
    
    def write_dep_js(self):
        source = u""
        config = self.load_app_json()
        for item in config["dependencies"]:
            source += "\n/*\n filename: %s \n*/" % item
            source += read_file(item)
        write_file(self.bin_dir(append="scripts/core.js"), source)
    
    def write_app_js(self):
        app_js = u""
        app_js += self.prep_config_js()
        app_js += self.prep_routes_js()
        app_js += self.prep_controller_js()
        write_file(self.bin_dir(append="scripts/app.js"), app_js)
    
    def write_html(self):
        styles = self.find_style_deps()
        scripts = ["scripts/core.js", "scripts/app.js"]
        self.write_html_index(scripts, styles)
    
    def partial(self, event):
        raise Exception("Partial builds are not supported in a production build.")
    
    def all(self, clean_proj=True):
        
        self.clean()
        
        self.write_app_js()
        self.write_dep_js()
        self.write_all_sass()
        self.write_sprites()
        self.copy_img()
        self.write_html()
    

