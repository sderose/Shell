#!/usr/bin/env python3
#
# pythonpath.py: Display and check where Python is going to look.
# 2014-06-12: Written by Steven J. DeRose.
#
import sys
import os
import re
import argparse
from subprocess import check_output, CalledProcessError
#import glob

from sjdUtils import sjdUtils
su = sjdUtils()
lg = su.getLogger()

__metadata__ = {
    "title"        : "pythonpath.py",
    "description"  : "Display and check where Python is going to look.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2014-06-12",
    "modified"     : "2021-06-16",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]


descr = """
=Usage=

Display `$PYTHONPATH`, and check that all the mentioned directories exist.
Also can check correspondence to sys.path, warn for duplicate mentions
of the same directory or class name, and find code that references or
modifies sys.path.

To search for a specific class(es), see ``--where`.


=Related Commands=

My `tracePythonPackage.py` checks sys.path directories and the lists
for various installers and package managers, to find who has a Python library.

My `showEnv` list everybody installed by a wide range of managers (Python
and other).


=To do=

* Option to find specific package.
* CATCH existing .pyc when there's no .py in same dir.
* Identify pip, port, brew, easy_install, etc.
* Hook up getClassDefs2()!!! TODO
* Check for files or classes defined at more than one place on path


=History=

* 2014-06-12: Written by Steven J. DeRose.
* 2014-07-10: Report missing __init__.py.
* 2014-09-09: Add --extras, --where, lg.info() indirection.
* 2015-08-06: Clean up options. Quieter by default. Finish --find x.
* 2020-11-06: Fix split().
* 2021-06-16: Fix some 'grep' issues.
* 2022-05-10: Switch to Python logger conventions.


=Rights=

Copyright 2014-06-12 by Steven J. DeRose. This work is licensed under a Creative
Commons Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[https://github.com/sderose].


=Options
"""

def hasPythonModule(curDir):
    if (os.path.exists(os.path.join(curDir,"__init__.py"))): return(True)
    subs = os.listdir(curDir)
    for sub in (subs):
        if (re.search(r"\.(py|pm|pyc)$", sub)): return(True)
    return(False)

def commonLen(a,b, onlyEndAt=""):
    """Find how much of the start of two strings is the same.
    If "wholeDirs" is set, only end at given character (e.g. "/")
    """
    n = min(len(a),len(b))
    for i in (range(0, n)):
        if (a[i] != b[i]):
            if (onlyEndAt == ""): return(i-1)
            if (onlyEndAt not in a[0:i]): return(i-1)
            lastSlash = a[0:i].rfind(onlyEndAt)
            return(lastSlash)
    return(n)


def getClassDefs(path, recursive=False):
    """Extract all the class definitions from a given file.
    For now, do this with "grep". Might be better to have Python actually
    parse the file, and then examine what externals have been defined.
    """
    print("Path: " + path)
    cmdTokens = [ "grep", "-H", "--include", "'*.py'", '"^class "', path ]
    if (recursive): cmdTokens.insert(1, "-r")
    #flist = glob.glob(path+"/*.py")
    #if (len(flist)<1): return("")
    #cmdTokens.extend(flist)
    lg.info("getClassDefs cmd: %s" % ("\\\n    ".join(cmdTokens)))
    bufRecs = []
    try:
        buf = check_output(cmdTokens, shell=False, stderr=None)
        if (isinstance(buf, str)):
            bufRecs = buf.split(sep="\n")
    except CalledProcessError as e:
        if ( e.returncode != 1 ):  # 1 is normal "nothing found"
            sys.stderr.write("CalledProcessError: %s\n" % (e))
    return(bufRecs)

def getClassDefs2(path):
    """A better way?
    Given a single file, find out what classes it defines.
    *** Should make a "list modules used, with paths" thing.
    Doc says that pyclbr.readmodule `pathList` arg "is used to augment
    the value of sys.path". In fact it is checked ""before"" sys.path,
    so can be used to check a specific file.
    """
    import pyclbr
    curDir, name = os.path.split(path)
    if (not name.endswith(".py")):
        raise ValueError
    name = name[0:-3]
    try:
        classDict = pyclbr.readmodule(name, path=curDir)
    except ImportError as e:
        lg.info("    Unable to access module '%s/%s': %s" % (curDir, name, e))
        return([])
    bigDict = {}
    for k, v in classDict.items():
        lg.info("    %-16s %-16s %s" % (k, v.module, v.file))
        if (k in bigDict):
            lg.info("    DUPLICATE %-16s %-16s %s" % (k, v.module, v.file))
            bigDict[k] += "\n" + v.file
        else:
            bigDict[k] = v.file
    return(bigDict)

def getClassDefsOfWholeDir(curDir):
    """A better way?
    Given a directory, find out what classes it defines.
    *** Should make a "list modules use with paths" thing.
    pyclbr.readmodule(moduleName, pathList) does what I want.
    Doc says that `pathList` "is used to augment the value of sys.path". In fact
    it is checked ""before"" sys.path, so can be used to check a specific file.
    """
    bigDict = {}
    for f in os.listdir(curDir):
        if (f.endswith(".pyc")):
            lg.warning0(".pyc found: %s/%s" % (curDir,f))
            continue
        elif (not f.endswith(".py")):
            continue
        classDict = getClassDefs2(os.path.join(curDir,f))
        for k, v in classDict.items():
            if (k in bigDict):
                print("    DUPLICATE %-16s %-16s %s" % (k, v.module, v.file))
                bigDict[k] += "\n" + v.file
            else:
                bigDict[k] = v.file
    return(bigDict)

def showClasses(curDir):
    """Find the specific classes defined by Python code in a given directory.
    """
    cds = getClassDefs(curDir)
    classesSeen = {}
    for cd in (cds):
        if (cd==""): continue
        if (args.where):
            if (re.search(args.where, cd)):
                lg.warning0("    *** FOUND *** %s" % (cd))
        else:
            lg.warning0("    ... %s" % (cd[len(curDir):]))
        if (cd in classesSeen):
            cl = re.sub(r"^.*class ", "", cd)
            lg.warning("        -- Duplicate def of class '%s'" % cl)
            classesSeen[cd] += "\n\t" + curDir
        else:
            classesSeen[cd] = curDir

    # Print dirs where multiply-defined classes were found
    for k,v in classesSeen.items():
        if (v.find("\n")>=0):
            print("%s:\n\t%s\n" % (k, v))
    return classesSeen

def checkPYTHONPATH():
    lg.info("Checking PYTHONPATH:")
    pp = os.environ["PYTHONPATH"]
    if (not pp):
        lg.fatal("Can't find $PYTHONPATH.")

    dirs = re.split(r":", pp)
    dirsSeen = {}
    classesSeen = {}
    lastD = ""
    for curDir in (dirs):
        if (args.classes): lg.info(0,"")
        if (args.abbrevs):
            clen = commonLen(lastD, curDir, onlyEndAt="/")
            printD = (" " * (clen+1)) + curDir[clen:]
        elif (args.color):
            clen = commonLen(lastD, curDir, onlyEndAt="/")
            printD = curDir[0:clen+1] + su.colorize(argColor="blue", s=curDir[clen:])
        else:
            printD = curDir
        lg.warning(printD)

        if (curDir in dirsSeen):
            lg.warning("    Duplicate PYTHONPATH entry '%s'" % (curDir))
        dirsSeen[curDir] = 1

        if (curDir == ""):
            lg.warning("    Empty entry")
            continue

        if (re.search(r"/\.\./|/\.|//|\$", curDir)):
            lg.warning("    Path is not normalized")
        if (not os.path.isdir(curDir)):
            lg.warning("    Directory does not exist", color="/red")
            continue
        if (args.init and
            not os.path.exists(os.path.join(curDir, "__init__.py"))):
            lg.warning("    Directory does not contain __init__.py", color="/red")
        if (not hasPythonModule(curDir)):
            lg.warning("    No modules found here")
        if (args.classes):
            showClasses(curDir)
        lastD = curDir
        # for each curDir
    return(dirs, dirsSeen, classesSeen)

def searchForFile(sysdirs, tgt):
    toss = open("/dev/null", mode="w")
    tgt += ".*"
    print("\nRunning finds for '%s'..." % (tgt))
    whereFound = []
    for curDir in sysdirs:
        fcmd = [ "find", curDir, "-name", tgt, "-print", "-maxdepth", "1" ]
        lg.info("Running: %s" % (" ".join(fcmd)))
        try:
            out = check_output(fcmd, stderr=toss)
            if (out.strip()): whereFound.append(out.strip())
        except CalledProcessError:
            pass  # Nothing found here
    return(whereFound)


###############################################################################
# Main
#
def processOptions():
    try:
        from BlockFormatter import BlockFormatter
        parser = argparse.ArgumentParser(
            description=descr, formatter_class=BlockFormatter)
    except ImportError:
        parser = argparse.ArgumentParser(description=descr)

    parser.add_argument(
        "--abbrevs", action="store_true",
        help="Leave out portion of each path that is the same as previous.")
    parser.add_argument(
        "--classes", action="store_true",
        help="Also report what classes are defined where.")
    colorDefault = (sys.stdout.isatty() and "CLI_COLOR" in os.environ)
    parser.add_argument(
        "--color", action="store_true", default=colorDefault,
        help="Use color to improve readability.")
    parser.add_argument(
        "--extras", "-x", action="store_true",
        help="Report any paths in $PYTHONPATH that aren't in sys.path.")
    parser.add_argument(
        "--find", type=str, metavar="T",
        help="Do 'find' for T.py under the given directory.")
    parser.add_argument(
        "--init", action="store_true",
        help="Report any paths with no __init__.py file.")
    parser.add_argument(
        "--pathmods", action="store_true",
        help="Search for code that modifies sys.path.")
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Suppress most messages.")
    parser.add_argument(
        "--sys", action="store_true",
        help="Report sys.path as well as path from environment.")
    parser.add_argument(
        "--verbose", "-v", action="count", default=0,
        help="Add more messages (repeatable).")
    parser.add_argument(
        "--version", action="version", version=__version__,
        help="Display version information, then exit.")
    parser.add_argument(
        "--where", type=str, default="", metavar="REGEX",
        help="Search for specific class or packge matching this regex.")

    args0 = parser.parse_args()
    return(args0)

classDefs = {}
args = processOptions()
su.setVerbose(args.verbose)
su.setColors(args.color)

if (args.where): args.classes = True

if ("PYTHONHOME" in os.environ):
    lg.warning0("Warning: $PYTHONHOME is set: '%s'." % (os.environ["PYTHONHOME"]))

dirs0, dirsSeen0, classesSeen0 = checkPYTHONPATH()
syspath = sys.path

if (args.sys or args.verbose):
    lg.warning0("%d in sys.path (indented ones are also in $PYTHONPATH):" %
        (len(syspath)))
    for sysDir in (syspath):
        if (sysDir in dirsSeen0): print("    "+sysDir)
        else: print(su.colorize(argColor="red", s=sysDir))

if (not (set(dirs0) < set(syspath))):
    lg.warning("\n$PYTHONPATH not a subset of sys.path. Extras:")
    xtra = set(dirs0)-set(syspath)
    lg.warning0("\n    ".join(xtra))

if (args.find):
    whereFound0 = searchForFile(syspath, args.find)
    for wh in whereFound0:
        print("    " + re.sub(r"\n", "\n    ", wh))

if (args.pathmods):
    print("\nSearching for code referring to sys.path.")
    for sysDir in (dirs0):
        x = check_output([ "grep", '-r "sys\\.path"', sysDir],
            stderr=None)
        if (x):
            print("\nUnder %s\n%x" % (sysDir,x))
