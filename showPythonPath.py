#!/usr/bin/env python3
#
# pypathShow.py: Show which python is really running, with what libs.
# 2021-09-09: Written by Steven J. DeRose.
#
import sys
import os

#from PowerWalk import PowerWalk, PWType

__metadata__ = {
    "title"        : "pypathShow.py",
    "description"  : "Show which python is really running, with what libs.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-09-09",
    "modified"     : "2021-09-09",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

Show which python is really running, with what libs.

The idea is to un-confuse interactions between python, PATH, PYTHONPATH, venv, poetry,
pip, conda,....


==Usage==

    pypathShow.py [options]


=Related Commands=


=Known bugs and Limitations=


=To do=


=History=

* 2021-09-09: Written by Steven J. DeRose.


=Rights=

Copyright 2021-09-09 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See [http://creativecommons.org/licenses/by-sa/3.0/] for more information.

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""


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
            "--libs", action="append", type=str, default=[],
            help="Report the location of this library. Repeatable.")
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
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        args0 = parser.parse_args()
        return(args0)


    ###########################################################################
    #
    args = processOptions()

    print("Python version: %s" % (sys.version))
    print("sys.path has:")
    for path in sys.path:
        print("    " + path)
    
    print("Location of selected libraries:")
    libs = [ 'os', 'penman', 'numpy' ]
    libs.extend(args.libs)
    for lib in libs:
        try:
            theModule = __import__(lib)
            print("    %-16s %s" % (lib, theModule.__file__))
        except ImportError:
            print("******* Cannot import '%s'." % (lib))
    
    # TODO: Say something about venv and conda state
    PathItems = os.environ['PATH'].split(sep=":")
    for p in PathItems:
        if ("venv" not in p): continue
        print("venv dir in PATH: %s" % (p))
        vPython = os.path.join(p, "python3")
        if (not os.path.exists(vPython)):
            print("venv does not have a python3 at '%s'." % (vPython))

    # Check for /usr/local/Cellar/poetry/ver
    # Check for /Library/Python/pyversionNumber
    # /usr/local/lib/python[ver]/site-packages
    # /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.8/lib/python3.8/site-packages
