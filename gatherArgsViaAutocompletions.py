#!/usr/bin/env python3
#
# gatherArgsViaAutocompletions.py: Use zsh autcomplete config to learn command args.
# 2021-09-10: Written by Steven J. DeRose.
#
from __future__ import print_function
import sys
import os
import codecs
#import string
#import math
#import subprocess
#from collections import defaultdict, namedtuple
#from typing import IO, Dict, List, Union

from PowerWalk import PowerWalk, PWType
#from sjdUtils import sjdUtils
#from alogging import ALogger
#su = sjdUtils()
#lg = ALogger(1)

__metadata__ = {
    "title"        : "gatherArgsViaAutocompletions.py",
    "description"  : "Use zsh autcomplete config to learn command args.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-09-10",
    "modified"     : "2021-09-10",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

Scan the files (generally one per command) that zsh uses to configure autcompletion.
Do a simple/approximate extraction of arguments for each, which can then be used
to generate:

* A command-line precis such as the "Usage" line in `man`.
* A matching set of `argparse` declarations
* A chart of args by command

This doesn't actually know the meaning of the args, it's just a simple syntactic
extraction (and far from a perfect one at that). The output should be reviewed and
edited before really depending on it.

==Usage==

    gatherArgsViaAutocompletions.py [options] [files]


=Related Commands and Files=

`autoload -Uz compinit && compinit` or `compinstall` -- typical commands to set up zsh autocompletion.

`/usr/share/zsh/[version]/functions` -- at least on MacOS, command definitions are here.


=Known bugs and Limitations=


=To do=


=History=

* 2021-09-10: Written by Steven J. DeRose.


=Rights=

Copyright 2021-09-10 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See [http://creativecommons.org/licenses/by-sa/3.0/] for more information.

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""

def log(lvl:int, msg:str) -> None:
    if (args.verbose >= lvl): sys.stderr.write(msg + "\n")
def warning0(msg:str) -> None: log(0, msg)
def warning1(msg:str) -> None: log(1, msg)
def warning2(msg:str) -> None: log(2, msg)
def fatal(msg:str) -> None: log(0, msg); sys.exit()


###############################################################################
#
def extractInfo(path:str) -> int:
    """Read and deal with one individual file.
    Most files has a single lines starting '_arguments' like:    
        _arguments \
          '-v[lowest possible]' \
          '-c[cutoff]:cutoff year:' \
          '*:time zone:_time_zone'
          
    and/or code to assemble a list for it like this (from '_find'): 
        if ! _pick_variant gnu=gnu unix --help; then
          arguments=(
            '(-A)-a[list entries starting with .]'
            '(-a)-A[list all except . and ..]'
            '-d[list directory entries instead of contents]'
            ...
        )
        if [[ "$OSTYPE" = (netbsd*|dragonfly*|freebsd*|openbsd*|darwin*) ]]; then
          arguments+=(
            '-T[show complete time information]'    
            ...
          )
        fi
    """
    try:
        fh = codecs.open(path, "rb", encoding=args.iencoding)
    except IOError as e:
        warning0("Cannot open '%s':\n    %s" % (path, e))
        return 0

    for rec in fh.readlines():
        recnum += 1
        if (args.tickInterval and (recnum % args.tickInterval == 0)):
            warning0("Processing record %s." % (recnum))
        if (rec == ""): continue  # Blank record
        rec = rec.rstrip()
        print(rec)
    if  (fh != sys.stdin): fh.close()
    return


###############################################################################
# Main
#
if __name__ == "__main__":
    import argparse
    def anyInt(x:str) -> int:
        return int(x, 0)

    def processOptions() -> argparse.Namespace:
        try:
            from BlockFormatter import BlockFormatter
            parser = argparse.ArgumentParser(
                description=descr, formatter_class=BlockFormatter)
        except ImportError:
            parser = argparse.ArgumentParser(description=descr)

        parser.add_argument(
            "--color",  # Don't default. See below.
            help="Colorize the output.")
        parser.add_argument(
            "--configDir", type=str, default="/usr/share/zsh/5.8/functions",
            help="Path to dir containing the autocomplete definition files.")
        parser.add_argument(
            "--iencoding", type=str, metavar="E", default="utf-8",
            help="Assume this character coding for input. Default: utf-8.")
        parser.add_argument(
            "--ignoreCase", "-i", action="store_true",
            help="Disregard case distinctions.")
        parser.add_argument(
            "--oencoding", type=str, metavar="E", default="utf-8",
            help="Use this character coding for output. Default: iencoding.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        if (0): parser.add_argument(
            "--recursive", action="store_true",
            help="Descend into subdirectories.")
        parser.add_argument(
            "--tickInterval", type=anyInt, metavar="N", default=10000,
            help="Report progress every n records.")
        parser.add_argument(
            "--unicode", action="store_const", dest="iencoding",
            const="utf8", help="Assume utf-8 for input files.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")

        PowerWalk.addOptionsToArgparse(parser)

        parser.add_argument(
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        args0 = parser.parse_args()
        if (args0.color == None):
            args0.color = ("USE_COLOR" in os.environ and sys.stderr.isatty())
        #lg.setColors(args0.color)
        #if (args0.verbose): lg.setVerbose(args0.verbose)
        return(args0)

    ###########################################################################
    #
    args = processOptions()

    if (not args.configDir):
        for x in os.listdir(configDir):
            extractInfo(x)
            
