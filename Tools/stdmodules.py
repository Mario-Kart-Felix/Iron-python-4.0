# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.

'''
OVERVIEW:
This script outputs a log file showing standard CPython modules which cannot be 
imported from IronPython.

USAGE:
    ipy stdmodules.py C:\Python35
'''

from   sys import argv, path
import nt
import sys


#--GLOBALS---------------------------------------------------------------------
LOG_FILE_BUSTED = open("STD_MODULES_BROKEN_UNDER_IP.log", "w")
LOG_FILE_OK     = open("STD_MODULES_OK_UNDER_IP.log", "w")
STDOUT_FAKE = open(__file__ + ".stdout.log", "w")
STDOUT_BAK = sys.stdout
FILE_LIST = [LOG_FILE_BUSTED, LOG_FILE_OK, STDOUT_FAKE]
VERBOSE = __name__=="__main__"
BROKEN_LIST = []
BLACKLIST = ['test', 'idlelib'] #Importing all tests takes too long

#--FUNCTIONS-------------------------------------------------------------------
def import_helper(mod_name):
    '''
    Helper function used to temporarily override stdout before importing
    a module.
    '''
    try:
        sys.stdout = STDOUT_FAKE
        __import__(mod_name)
    finally:
        sys.stdout = STDOUT_BAK
             
                
def is_package(dir_name):
    '''
    Returns True if dir_name is actually a Python package in the current
    working directory.
    '''
    #*.py, *.pyd, etc
    if "." in dir_name:
        return False        
    
    #Make sure it exists
    try:
        if not nt.stat(dir_name): return False
    except:
        return False
    
    #Make sure it has an __init__.py
    try:
        if "__init__.py" not in nt.listdir(nt.getcwd() + "\\" + dir_name):
            return False
    except:
        return False
        
    return True


def log_broken(name, e):
    global BROKEN_LIST
    
    if VERBOSE:
        print(name, "FAILED")
    print("----------------------------------------------------------------", file=LOG_FILE_BUSTED)
    print("--", name, file=LOG_FILE_BUSTED)
    if hasattr(e, "clsException"):
        print(e.clsException, file=LOG_FILE_BUSTED)
    else:
        print(e, file=LOG_FILE_BUSTED)
    
    temp_name = name.replace(".", "\\")
    try:
        if nt.stat(CPY_LIB_DIR + "\\" + temp_name + ".py"):
            BROKEN_LIST.append("/Lib/" + temp_name.replace("\\", "/") + ".py")
    except:
        pass
    try:
        if nt.stat(CPY_LIB_DIR + "\\" + temp_name):
            BROKEN_LIST.append("/Lib/" + temp_name.replace("\\", "/"))
            BROKEN_LIST.append("/Lib/" + temp_name.replace("\\", "/") + "/__init__.py")
    except:
        pass    

def log_ok(name):
    if VERBOSE:
        print(name, "PASSED")    
    print(name, file=LOG_FILE_OK)


def check_package(package_name):
    '''
    Checks all subpackages and modules in the package_name package.
    '''
    cwd = nt.getcwd()
    
    if cwd==CPY_LIB_DIR:
        root_name = package_name
    else:
        root_name = cwd.split(CPY_DIR + "\\Lib\\")[1].replace("\\", ".") + "." + package_name
    
    #First check that the root package can be imported 
    try:
        import_helper(package_name)    
        log_ok(root_name)
        
    except (Exception, SystemExit) as e:
        log_broken(root_name, e)
        
        # no sense continuing
        return
    
    #Next examine subpackages and modules
    nt.chdir(cwd + "\\" + package_name)        
    
    for x in nt.listdir("."):
        if x.endswith(".py") and x not in ("__init__.py", '__main__.py'):
            x = x.split(".py", 1)[0]
            mod_name = nt.getcwd().split(CPY_DIR + "\\Lib\\")[1] + "\\" + x
            mod_name = mod_name.replace("\\", ".")
        
            try:
                import_helper(mod_name)   
                log_ok(mod_name) 
        
            except (Exception, SystemExit) as e:
                log_broken(mod_name, e)
        
        elif is_package(x) and not x.startswith('test'):
            check_package(x)

    nt.chdir(cwd)

#--MAIN------------------------------------------------------------------------
def main(cpy_dir):
    global CPY_DIR
    global CPY_LIB_DIR
    
    CPY_DIR = cpy_dir
    CPY_LIB_DIR = cpy_dir + "\\Lib"  #E.g., C:\Python35\Lib
    
    path.append(CPY_LIB_DIR)
    path.insert(0, ".")


    print("------------------------------------------------------------------------")
    print("--PACKAGES")
    cwd = nt.getcwd()
    nt.chdir(CPY_LIB_DIR)

    for pack_name in nt.listdir(CPY_LIB_DIR):
        if not is_package(pack_name):
            continue
        elif pack_name in BLACKLIST:
            continue
        
        check_package(pack_name)
    print()

    nt.chdir(cwd)
    
    print("------------------------------------------------------------------------")
    print("--MODULES")
    
    for x in nt.listdir(CPY_LIB_DIR):
        if x.endswith(".py"):
            mod_name = x.split(".py", 1)[0]
        else:
            continue
            
        try:
            import_helper(mod_name)   
            log_ok(mod_name) 
            
        except Exception as e:
            log_broken(mod_name, e)
    
            
    #Cleanup        
    for f in FILE_LIST:
        f.close()

    return BROKEN_LIST

if __name__=="__main__":
    main(sys.argv[1])
