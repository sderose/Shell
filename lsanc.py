#!/usr/bin/env python3
#
# lsanc.py: Show permissions for all ancestors.
# 2021-08-31: Written by Steven J. DeRose.
#
import sys
import os
from os import stat as osstat
import stat

#from PowerStat import PowerStat, statFormats

__metadata__ = {
    "title"        : "lsanc.py",
    "description"  : "Show permissions for all ancestors.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-08-31",
    "modified"     : "2021-09-01",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

Given a file or directory, show the permissions for it and for each ancestor directory.
This is useful for finding whether an ancestor directory is blocking some kind of access.

==Usage==

    lsanc.py [options] [files]


=Related Commands=


=Known bugs and Limitations=

If you ask about multiple files, it doesn't suppress repetition of common ancestors.


=To do=

Hook up to PowerStat.py for more flexible reporting.


=History=

* 2021-08-31: Written by Steven J. DeRose. But I wrote this ages ago, first as a bash
shell function, then a bash script. But the escaping and quoting for paths with spaces
got too ugly.


=Rights=

Copyright 2021-08-31ff by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See [http://creativecommons.org/licenses/by-sa/3.0/] for more information.

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""
args = None

def log(lvl:int, msg:str) -> None:
    if (args is None or args.verbose >= lvl): sys.stderr.write(msg + "\n")
def warning0(msg:str) -> None: log(0, msg)
def warning1(msg:str) -> None: log(1, msg)
def warning2(msg:str) -> None: log(2, msg)
def fatal(msg:str) -> None: log(0, msg); sys.exit()


###############################################################################
#
#myFormat = statFormats["ls_l"]
#warning0("Chosen format: %s" % (myFormat))
#ps = PowerStat(myFormat)

def doOneFile(path:str) -> int:
    """Deal with one individual file.
    """
    ap = os.path.abspath(path)
    if (not os.path.exists(ap)):
        warning0("File not found: %s" % (ap))
        return

    parts = ap.split(sep="/")[0:]
    #warning1("Parts: [ '%s' ]" % ("', '".join(parts)))
    curPath = "/"
    for part in parts:
        curPath = os.path.join(curPath, part)
        printFileInfo(curPath)

def printFileInfo(path):
    statResult = osstat(path)
    warning1("statResult: " + repr(statResult))
    stMode = statResult.st_mode
    warning1("stMode: " + repr(stMode))
    perms = stat.filemode(stMode)
    print("%9s %s" % (perms, path))    
    
       
###############################################################################
# Main
#
if __name__ == "__main__":
    import argparse

    def processOptions() -> argparse.Namespace:
        try:
            from BlockFormatter import BlockFormatter
            parser = argparse.ArgumentParser(
                description=descr, formatter_class=BlockFormatter)
        except ImportError:
            parser = argparse.ArgumentParser(description=descr)

        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")

        parser.add_argument(
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        args0 = parser.parse_args()
        return(args0)

    ###########################################################################
    #
    args = processOptions()

    if (len(args.files) == 0):
        fatal("lsanc.py: No files specified....")

    for path0 in args.files:
        print()
        doOneFile(path0)
