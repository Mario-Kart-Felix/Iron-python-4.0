# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.

'''
OVERVIEW:
Cleans a directory full of tests.

USAGE:
    ipy cleantests.py C:\...\IronPython\Tests
'''
from   sys import argv
import nt
import re

#--GLOBALS---------------------------------------------------------------------
DEBUG = False

TEST_DIR = argv[1]
THIS_MOD = __file__.rsplit("\\", 1)[1]
TESTS = [x for x in nt.listdir(TEST_DIR) if x.endswith(".py") and x!=THIS_MOD]
if DEBUG:
    print("TESTS:", TESTS)

TF_DIR = nt.environ["DevEnvDir"] + r"\tf"
TFPT_DIR = nt.environ["DLR_ROOT"] + r"\Util\tfpt\tfpt.exe"

#--FUNCTIONS-------------------------------------------------------------------
def apply_filters(lines):
    for filter in [strip_ws, tabs_are_bad]:
        list(filter(lines))

def strip_ws(lines):
    for i in range(len(lines)):
        #If the line doesn't consist exclusively of WS
        if re.match("^[\s]*$", lines[i])==None:
            lines[i] = lines[i].rstrip() + "\n"

def tabs_are_bad(lines):
    for i in range(len(lines)):
        if (re.match("^\t", lines[i])!=None):
            lines[i] = re.sub("\t", "    ", lines[i])
    
#--MAIN------------------------------------------------------------------------
nt.chdir(TEST_DIR)

for test in TESTS:
    #Get the contents of the file
    f = open(test, "r")
    lines = f.readlines()
    f.close()

    #Fix the file
    apply_filters(lines)
    
    #Check out the file
    try:
        ec = nt.spawnv(nt.P_WAIT, TF_DIR, ["tf", "edit", test])
    except Exception as e:
        print("FAILED: could not check out %s from TFS: %s" % (test, str(e)))
        continue
    
    if ec!=0:
        print("FAILED: could not check out %s from TFS!" % test)
        continue
        
    #Write it back out
    f = open(test, "w")
    f.writelines(lines)
    f.close()
    
    
#Cleanup
ec = nt.spawnv(nt.P_WAIT, TFPT_DIR, ["tfpt", "uu", TEST_DIR])        
if ec!=0:
    print("FAILED: could not tf undo files that were never changed in %s!" % TEST_DIR)
