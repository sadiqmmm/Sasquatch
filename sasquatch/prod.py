from dev import DevBuild
from util import *
import sys, re
from jsmin import jsmin

class ProdBuild(DevBuild):
    
    def minify_js(self, input_f, output):
        print input_f, output
        compiler.minify_js(input_f, output)
    
    def minify_css(self, css):
        '''
        taken from http://stackoverflow.com/questions/222581/python-script-for-minifying-css
        '''
        # remove comments - this will break a lot of hacks :-P
        css = re.sub( r'\s*/\*\s*\*/', "$$HACK1$$", css ) # preserve IE<6 comment hack
        css = re.sub( r'/\*[\s\S]*?\*/', "", css )
        css = css.replace( "$$HACK1$$", '/**/' ) # preserve IE<6 comment hack

        # url() doesn't need quotes
        css = re.sub( r'url\((["\'])([^)]*)\1\)', r'url(\2)', css )

        # spaces may be safely collapsed as generated content will collapse them anyway
        css = re.sub( r'\s+', ' ', css )

        # shorten collapsable colors: #aabbcc to #abc
        css = re.sub( r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', css )

        # fragment values can loose zeros
        css = re.sub( r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', css )

        for rule in re.findall( r'([^{]+){([^}]*)}', css ):

            # we don't need spaces around operators
            selectors = [re.sub( r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip() ) for selector in rule[0].split( ',' )]

            # order is important, but we still want to discard repetitions
            properties = {}
            porder = []
            for prop in re.findall( '(.*?):(.*?)(;|$)', rule[1] ):
                key = prop[0].strip().lower()
                if key not in porder: porder.append( key )
                properties[ key ] = prop[1].strip()
        
        return css
    
    
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
        if self.has_shared():
            spartial_dir = self.shared_dir("partial")
            source += self.__prep_controller_js(spartial_dir, True)
        return source
    
    def write_dep_js(self):
        print "writing core.js..."
        source = u""
        config = self.load_app_json()
        for item in config["dependencies"]:
            print "minifying: %s" % item
            if item.find("[shared]") == 0:
                basename = item[8:]
                item = self.shared_dir(basename)
            source += read_file(item) + "\n\n\n"
        core_js_file = self.bin_dir(append="scripts/core.js")
        write_file(core_js_file+"s", source)
        self.minify_js(core_js_file+"s", core_js_file)
    
    def write_app_js(self):
        print "writing app.js..."
        app_js = u""
        app_js += self.prep_config_js()
        app_js += self.prep_routes_js()
        app_js += self.prep_controller_js()
        app_js_file = self.bin_dir(append="scripts/app.js")
        write_file(app_js_file+"s", app_js)
        self.minify_js(app_js_file+"s", app_js_file)
    
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
        
        #generate sprites
        self.copy_img()
        self.copy_standalone_sass()
        self.combine_app_sass()
        self.write_sprites()
        self.run_compass()
        self.write_html()
    

