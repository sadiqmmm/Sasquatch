import codecs, os, subprocess
from multiprocessing import Process

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

def copy_file(start, end):
    t = read_file(start)
    write_file(end, t)

def copytree(src, dst):
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                copy_file(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.append(err.args[0])
        
    if len(errors) > 0:
        raise Exception(errors)

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

############################
##  External Process
############################

def __external_process__(*args):
    subprocess.call(args)

def external_process(*args):
    p = Process(target=__external_process__, args=args)
    p.start()
    p.join()


