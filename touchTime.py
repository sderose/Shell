#!/usr/bin/env python3
#
# touchTime.py: Set the mod-time of a file via "touch", but a little handier.
# 2021-10-05: Written by Steven J. DeRose.
#
import sys
import codecs

from PowerWalk import PowerWalk, PWType

__metadata__ = {
    "title"        : "touchTime.py",
    "description"  : "Set the mod-time of a file via 'touch', but a little handier.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-10-05",
    "modified"     : "2021-10-05",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

==Usage==

Unfinished.

    touchTime.py [options] [files]

Set the mod-time of a file via "touch", but a little handier.

Actions:
    * Exclude certain days or times of day
    * Force into certain days or times of day
    * Pin to a min or max
    * Pin to nearest ok date/time, or random within a range around it
    * Set to equal, precede, or follow another file's time
    * Support UTC or localtimes.
    
Note: All this can be done via `touch`, this just saves some arithmetic.


=Related Commands=


=Known bugs and Limitations=


=To do=

Finish.


=History=

* 2021-10-05: Written by Steven J. DeRose.


=Rights=

Copyright 2021-10-05 by Steven J. DeRose. This work is licensed under a
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
def error(msg:str) -> None: log(0, msg)
def fatal(msg:str) -> None: log(0, msg), sys.exit()


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
            fh = codecs.open(path, "rb", encoding=args.iencoding)
        except IOError as e:
            warning0("Cannot open '%s':\n    %s" % (path, e))
            return 0

    recnum = 0
    for rec in fh.readlines():
        recnum += 1
        if (args.tickInterval and (recnum % args.tickInterval == 0)):
            warning0("Processing record %s." % (recnum))
        if (rec == ""): continue  # Blank record
        rec = rec.rstrip()
        print(rec)
    if (fh != sys.stdin): fh.close()
    return recnum

def doOneXmlFile(path):
    """Parse and load
    """
    from xml.dom import minidom
    from DomExtensions import DomExtensions
    DomExtensions.patchDom(minidom)
    xdoc = minidom.parse(path)
    docEl = xdoc.documentElement
    paras = docEl.getElementsByTagName("P")
    for para in paras:
        print(para.textValue)
    return 0


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
            "--ignoreCase", "-i", action="store_true",
            help="Disregard case distinctions.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
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
        return(args0)

    ###########################################################################
    #
    args = processOptions()

    if (len(args.files) == 0):
        warning0("touchTime.py: No files specified....")
        sys.exit()

    pw = PowerWalk(args.files, open=False, close=False)
    pw.setOptionsFromArgparse(args)
    for path0, fh0, what0 in pw.traverse():
        if (what0 != PWType.LEAF): continue
        if (path0.endswith(".xml")): doOneXmlFile(path0)
        else: doOneFile(path0)
    if (not args.quiet):
        warning0("touchTime.py: Done, %d files.\n" % (pw.getStat("regular")))
