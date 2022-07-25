#!/usr/bin/env python3
#
# wcPP.py: A slightly smarter version of 'wc' (word-count).
# 2022-02-24: Written by Steven J. DeRose.
#
from __future__ import print_function
import sys
import os
import re
from xml.dom.minidom import Node
#from typing import IO, Dict, List, Union

from PowerWalk import PowerWalk, PWType

import logging
lg = logging.getLogger("wcPP.py")
def info0(msg:str) -> None:
    if (args.verbose >= 0): lg.info(msg)
def info1(msg:str) -> None:
    if (args.verbose >= 1): lg.info(msg)
def info2(msg:str) -> None:
    if (args.verbose >= 2): lg.info(msg)
def fatal(msg:str) -> None: 
    lg.critical(msg); sys.exit()

__metadata__ = {
    "title"        : "wcPP.py",
    "description"  : "A slightly smarter version of 'wc' (word-count).",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2022-02-24",
    "modified"     : "2022-02-24",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Name=
    """ +__metadata__["title"] + ": " + __metadata__["description"] + """
    
=Description=

A slightly smarter version of 'wc' (word-count). Specifically:

* -c counts ''characters'', not bytes. -m also works, as in 'wc'. 
* -b counts bytes, instead of the usual -c.
* Can handle many character encodings (--iencoding).
* Can omit the filename(s). This is easier to use in shell script assignments.
* Can provide individual file counts, the grand total, or both, at option.
* Provides the full file-selection power of PowerWalk.
* Has both short and long option names.

If none of -b, -c, -l, or -w is specified, all will be counted.

If neither -c nor -w is active, no attempt is made to decode the input text.

Output goes in the order: line, word, character, byte, and filename.
==Usage==

    wcPP.py [options] [files]


=See also=


=Known bugs and Limitations=

* XML and HTML files are identified merely by extension.
* Perhaps should check POSIXLY_COMPLIANT and support -c for bytes.


=To do=

* Provide several alternative definitions for "words" to count. At the moment, just
splits on \\s+.
* Learn more file formats and count just "text" in them
MarkDown, POD, etc).
* Add a strftime-like format-string option.


=History=

* 2022-02-24: Written by Steven J. DeRose.


=Rights=

Copyright 2022-02-24 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See [http://creativecommons.org/licenses/by-sa/3.0/] for more information.

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""


###############################################################################
#
totals = {
    'byte': 0,
    'char': 0,
    'word': 0,
    'line': 0,
}

grandTotals = totals.copy()

def clearTotals():
    for k in totals.keys():
        totals[k] = 0

def countRec(path:str, recnum:int, rec:str):
    totals["line"] += 1
    totals["byte"] += len(rec)
    if (args.characters or args.words):
        try:
            txt = rec.decode(args.iencoding)
        except Exception as e:
            lg.warning("%s:%d: Decoding problem:\n    %s", path, recnum, e)
            return
        totals["char"] += len(txt)
        totals["word"] += len(tokenize(txt))

def tokenize(s:str) -> list:
    # TODO Overly simplistic...
    return re.split(r"\s+", s)
    
def report(tots:dict, filename:str):
    buf = ""
    if (args.line):      buf += "%6d" % (tots["line"])
    if (args.word):      buf += "%6d" % (tots["word"])
    if (args.character): buf += "%6d" % (tots["char"])
    if (args.byte):      buf += "%6d" % (tots["byte"])
    if (args.filename):  buf += "%s" % (filename)
    print(buf)
    
    
###############################################################################
#
def doOneFile(path:str) -> int:
    """Read and deal with one individual file.
    """
    if (not path):
        if (sys.stdin.isatty()): print("Waiting on STDIN...")
        fh = sys.stdin
    else:
        try:
            fh = open(path, "rb")
        except IOError as e:
            info0("Cannot open '%s':\n    %s" % (path, e))
            return 0

    clearTotals()
    for recnum, rec in enumerate(fh.readlines()):
        countRec(path, recnum, rec)
    if  (fh != sys.stdin): fh.close()
    return totals

def doOneXmlFile(path:str):
    """Parse and load
    """
    from xml.dom import minidom
    from DomExtensions import DomExtensions
    DomExtensions.patchDom(minidom.Node)
    xdoc = minidom.parse(path)
    docEl = xdoc.documentElement
    for nodeNum, txt in enumerate(getTextNodes(docEl)):
        countRec(path, nodeNum, txt)
    return totals

def getTextNodes(node:Node) -> str:
    if (node.nodeType in [ Node.TEXT_NODE, Node.CDATA_SECTION_NODE ]):
        yield node.data
    elif (node.nodeType == Node.ELEMENT_NODE):
        for ch in node.childNodes:
            yield getTextNodes(ch)
    return
    
    
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
            "--iencoding", type=str, metavar="E", default="utf-8",
            help="Assume this character coding for input. Default: utf-8.")
        parser.add_argument(
            "--bytes", "-b", action="store_true",
            help="Count bytes.")
        parser.add_argument(
            "--characters", "--chars", "=m", "-c", action="store_true",
            help="Count characters (see also --iencoding).")
        parser.add_argument(
            "--filenames", "-f", action="store_true",
            help="Display individual file names (the default).")
        parser.add_argument(
            "--no-filenames", "--nf", "-n", action="store_false", dest="fileNames",
            help="Do NOT display individual file names.")
        parser.add_argument(
            "--grandTotals", "-g", action="store_true",
            help="Display grand totals across all input files (default).")
        parser.add_argument(
            "--no-grandTotals", "--ng", action="store_false", dest="grandTotals",
            help="Display grand totals across all input files (default).")
        parser.add_argument(
            "--lines", "-l", action="store_true",
            help="Count lines.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "--unicode", action="store_const", dest="iencoding",
            const="utf8", help="Assume utf-8 for input files.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")
        parser.add_argument(
            "--words", "-", action="store_true",
            help="Count words, according to a rudimentary definition.")

        PowerWalk.addOptionsToArgparse(parser)

        parser.add_argument(
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        if (not (args.bytes | args.characters | args.words | args.lines)):
            args.bytes = args.characters = args.words = args.lines = True
            
        args0 = parser.parse_args()
        return(args0)

    ###########################################################################
    #
    args = processOptions()

    if (len(args.files) == 0):
        info0("wcPP.py: No files specified....")
        doOneFile(None)
    else:
        pw = PowerWalk(args.files, open=False, close=False,
            encoding=args.iencoding)
        pw.setOptionsFromArgparse(args)
        for path0, fh0, what0 in pw.traverse():
            if (what0 != PWType.LEAF): continue
            _name, ext = os.path.splitext(path0)
            if (ext in [ ".xml", ".html", ".htm" ]):
                doOneXmlFile(path0)
            else:
                doOneFile(path0)
            report(totals, path0)
            for gtk in grandTotals.keys():
                grandTotals[gtk] += totals[gtk]
        
        if (args.grandTotals):
            report(grandTotals, args.grandLabel)
        if (not args.quiet):
            info0("wcPP.py: Done, %d files.\n" % (pw.getStat("regular")))
