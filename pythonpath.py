#!/usr/bin/env python
#
# pythonpath -- display and check where Python is going to look.
#
from __future__ import print_function
import sys
import os
import re
import argparse
#import string
import subprocess
import glob

from sjdUtils import sjdUtils
from MarkupHelpFormatter import MarkupHelpFormatter

__metadata__ = {
    'title'        : "pythonpath.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2014-06-12",
    'modified'     : "2020-03-01",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Usage=

Display $PYTHONPATH, and check that all the mentioned directories exist.
Also can check correspondence to sys.path, and warn for duplicate mentions
of the same directory or class name.

It is also useful to try 'find . -name '*.py'.

=Notes=

* 2014-06-12: Written by Steven J. DeRose.

* 2014-07-10: Report missing __init__.py.

* 2014-09-09: Add --extras, --where, notify() indirection.

* 2015-08-06: Clean up options. Quieter by default. Finish --find x.

=To do=

* CATCH existing .pyc when there's no .py in same dir!

* Identify pip, port, brew, easy_install

* Hook up getClassDefs2()!!! FIX

* Check for file, or even classes, defined at more than one place on path

* Check for more module conventions?

* CF: findExternals.py.

=Rights=

This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[http://github.com/sderose].

=Options
""",

args = None
su = sjdUtils()
lg = su.getLogger()


def notify(level, msg, color=None):
    if (args.where): return
    if (color): lg.vMsg(level, msg, color=color)
    else: lg.vMsg(level, msg)

def prob(level, msg, color='red'):
    if (args.where): return
    if (color): lg.vMsg(level, msg, color=color)
    else: lg.vMsg(level, msg)


def hasPythonModule(curDir):
    if (os.path.exists(os.path.join(curDir,"__init__.py"))): return(True)
    subs = os.listdir(curDir)
    for sub in (subs):
        if (re.search(r'\.(py|pm|pyc)$', sub)): return(True)
    return(False)

def commonLen(a,b, onlyEndAt=''):
    """Find how much of the start of two strings is the same.
    If 'wholeDirs' is set, only end at given character (e.g. '/')
    """
    n = min(len(a),len(b))
    for i in (range(0, n)):
        if (a[i] != b[i]):
            if (onlyEndAt == ''): return(i-1)
            if (onlyEndAt not in a[0:i]): return(i-1)
            lastSlash = a[0:i].rfind(onlyEndAt)
            return(lastSlash)
    return(n)


def getClassDefs(path, recursive=False):
    """Extract all the class definitions from a given file.
    For now, do this with 'grep'. Might be better to have Python actually
    parse the file, and then examine what externals have been defined.
    """
    cmdTokens = [ "grep", "-H", "'^class '" ]
    if (recursive): cmdTokens.insert(1, "-r")
    flist = glob.glob(path+'/*.py')
    if (len(flist)<1): return("")
    cmdTokens.extend(flist)
    lg.vMsg(1, "getClassDefs cmd: %s" % ("\\\n    ".join(cmdTokens)))
    try:
        buf = subprocess.check_output(cmdTokens, shell=False, stderr=None)
        if (type(buf) == type('x')):
            bufRecs = "\n".split(buf)
    except Exception as e:
        sys.stderr.write("Exception: %s" % (e))
        bufRecs = []
    return(bufRecs)

def getClassDefs2(path):
    """A better way?
    Given a single file, find out what classes it defines.
    *** Should make a "list modules used, with paths" thing.
    Doc says that pyclbr.readmodule F<pathList> arg "is used to augment
    the value of sys.path". In fact it is checked I<before> sys.path,
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
        lg.vMsg(1, "    Unable to access module '%s/%s': %s" % (curDir, name, e))
        return([])
    bigDict = {}
    for k, v in classDict.items():
        lg.vMsg(1, "    %-16s %-16s %s" % (k, v.module, v.file))
        if (k in bigDict):
            lg.vMsg(1, "    DUPLICATE %-16s %-16s %s" % (k, v.module, v.file))
            bigDict[k] += "\n" + v.file
        else:
            bigDict[k] = v.file
    return(bigDict)

def getClassDefsOfWholeDir(curDir):
    """A better way?
    Given a directory, find out what classes it defines.
    *** Should make a "list modules use with paths" thing.
    pyclbr.readmodule(moduleName, pathList) does what I want.
    Doc says that F<pathList> "is used to augment the value of sys.path". In fact
    it is checked I<before> sys.path, so can be used to check a specific file.
    """
    bigDict = {}
    for f in os.listdir(curDir):
        if (f.endswith(".pyc")):
            lg.vMsg(0, ".pyc found: %s/%s" % (curDir,f))
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
    lg.MsgPush()
    classesSeen = {}
    for cd in (cds):
        if (cd==''): continue
        if (args.where):
            if (re.search(args.where, cd)):
                lg.vMsg(0, "*** FOUND *** %s" % (cd))
        else:
            lg.vMsg(0, "... %s" % (cd[len(curDir):]))
        if (cd in classesSeen):
            cl = re.sub(r'^.*class ','',cd)
            prob(0, "    -- Duplicate def of class '%s'" % cl)
            classesSeen[cd] += "\n\t" + curDir
        else:
            classesSeen[cd] = curDir
    lg.MsgPop()
    # Print dirs where multiply-defined classes were found
    for k,v in classesSeen.items():
        if (v.find("\n")>=0):
            print("%s:\n\t%s\n" % (k, v))
    return()


###############################################################################
# Process options
#
def processArgs():
    parser = argparse.ArgumentParser(
        description=descr,
        formatter_class=MarkupHelpFormatter
    )
    parser.add_argument(
        "--abbrevs",         action='store_true',
        help='Leave out portion of each path that is the same as previous.')
    parser.add_argument(
        "--classes",         action='store_true',
        help='Also report what classes are defined where.')
    colorDefault = (sys.stdout.isatty() and "USE_COLOR" in os.environ)
    parser.add_argument(
        "--color",           action='store_true',   default=colorDefault,
        help='Use color to improve readability.')
    parser.add_argument(
        "--extras", "-x",     action='store_true',
        help='Report any paths in $PYTHONPATH that aren\'t in sys.path.')
    parser.add_argument(
        "--find",            type=str, metavar="T",
        help='Do "find" for  T.py under the given directory.')
    parser.add_argument(
        "--init",            action='store_true',
        help='Report any paths with no __init__.py file.')
    parser.add_argument(
        "--pathmods",       action='store_true',
        help='Search for code that modifies sys.path.')
    parser.add_argument(
        "--quiet", "-q",     action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--sys",             action='store_true',
        help='Report sys.path as well as path from environment.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        '--version',          action='version', version=__metadata__['__version__'],
        help='Display version information, then exit.')
    parser.add_argument(
        '--where',            type=str,             default="",
        help='Search for a specific class or packge and report curDir(s).')

    args0 = parser.parse_args()
    return(args0)


def checkPYTHONPATH():
    notify(0, "Checking PYTHONPATH:")
    pp = os.environ["PYTHONPATH"]
    if (not pp):
        lg.warn(-1, "Can't find $PYTHONPATH.")

    dirs = re.split(r':', pp)
    dirsSeen = {}
    classesSeen = {}
    lastD = ""
    for curDir in (dirs):
        if (args.classes): notify(0,"")
        if (args.abbrevs):
            clen = commonLen(lastD, curDir, onlyEndAt='/')
            printD = (" " * (clen+1)) + curDir[clen:]
        elif (args.color):
            clen = commonLen(lastD, curDir, onlyEndAt='/')
            printD = curDir[0:clen+1] + su.colorize("blue", curDir[clen:])
        else:
            printD = curDir
        notify(0, printD)

        if (curDir in dirsSeen):
            prob(0, "    Duplicate PYTHONPATH entry '%s'" % (curDir))
        dirsSeen[curDir] = 1

        if (curDir == ""):
            prob(0, "    Empty entry")
            continue

        if (re.search(r'/\.\./|/\.|//|\$', curDir)):
            prob(0, "    Path is not normalized")
        if (not os.path.isdir(curDir)):
            prob(0, "    Directory does not exist", color='/red')
            continue
        if (args.init and
            not os.path.exists(os.path.join(curDir,"__init__.py"))):
            prob(0, "    Directory does not contain __init__.py", color='/red')
        if (not hasPythonModule(curDir)):
            prob(0, "    No modules found here")
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
        fcmd = [ 'find', curDir, '-name', tgt, '-print', '-maxdepth', '1' ]
        lg.vMsg(2, "Running: %s" % (" ".join(fcmd)))
        try:
            out = subprocess.check_output(fcmd, stderr=toss)
            if (out.strip()): whereFound.append(out.strip())
        except subprocess.CalledProcessError:
            pass  # Nothing found here
    return(whereFound)


###############################################################################
###############################################################################
# Main
#
classDefs = {}
args = processArgs()
su.setVerbose(args.verbose)
su.setColors(args.color)

if (args.where): args.classes = True

if ("PYTHONHOME" in os.environ):
    lg.warn(0, "Warning: $PYTHONHOME is set, to " + os.environ["PYTHONHOME"])

dirs0, dirsSeen0, classesSeen0 = checkPYTHONPATH()
syspath = sys.path

if (args.sys or args.verbose):
    lg.hMsg(0, "%d in sys.path (indented ones are also in $PYTHONPATH):" %
        (len(syspath)))
    for sysDir in (syspath):
        if (sysDir in dirsSeen0): print("    "+sysDir)
        else: print(su.colorize("red", sysDir))

if (not (set(dirs0) < set(syspath))):
    prob(0, "\n$PYTHONPATH not a subset of sys.path. Extras:")
    xtra = set(dirs0)-set(syspath)
    lg.vMsg(0, "\n    ".join(xtra))

if (args.find):
    whereFound0 = searchForFile(syspath, args.find)
    for wh in whereFound0:
        print("    " + re.sub(r'\n', '\n    ', wh))

if (args.pathmods):
    print("\nSearching for code referring to sys.path.")
    for sysDir in (dirs0):
        x = subprocess.check_output([ 'grep', '-r "sys\\.path"', sysDir],
            stderr=None)
        if (x):
            print("\nUnder %s\n%x" % (sysDir,x))

lg.vMsg(0, "Done.")

sys.exit(0)
