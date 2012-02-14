import codecs, os

############################
##  File Utilities
############################

def read_file(location):
    f = codecs.open(location, encoding='utf-8', mode="rb")
    result = f.read()
    f.close()
    return result

def write_file(location, txt):
    f = codecs.open(location, encoding='utf-8', mode="wb")
    f.write(txt)
    f.close()


############################
##  File References 
############################

def project_dir(append=None):
    base = os.getcwd()
    print "BASE >> %s " % base
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
