#!/usr/bin/env python
#
# tracePythonPackage.py
#
# 2018-05-18: Written. Copyright by Steven J. DeRose.
# Creative Commons Attribution-Share-alike 3.0 unported license.
# See http://creativecommons.org/licenses/by-sa/3.0/.
#
from __future__ import print_function
import sys, os
import argparse
#import re
from subprocess import check_output

from MarkupHelpFormatter import MarkupHelpFormatter

__metadata__ = {
    'title'        : "ColorManager.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2018-05-18",
    'modified'     : "2020-03-01",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Description=

Look all over the place to see where Python is getting a given package
(packages whose name I<contains> the requested string are also reported).

Python package managers included:

    PYTHONPATH itself
    pip
    port
    conda
    brew

B<Note>: A package manager's name for something, is often not the same as the
name you import. For example, you would import "sklearn", but it lives in
a package called "scikit-learn" (which you cannot import, but only install).

This command does not know about `PyPM`, `EasyInstall`, `Virtualenv`,
or the meta-manager `pyenv`.

Apparently Python will only resolve `import pkg` if:

* pkg does *not* include the ".py" extension

* the file *does* have extension ".py" (not even ".pyc")

* the file cannot be in a subdirectory of the PYTHONPATH dir specified
(and you can't specify the path in the import statement, either).


=Related Commands=

`identifyAllExecutables` -- search `PATH` for executables of a given name,
as well as reporting shell functions, aliases,shell keywords, and builtins.

=Known bugs and Limitations=

Probably should also be able to list the versions of the package managers.

=Rights=

Copyright 2015 by Steven J. DeRose.
This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[http://github.com/sderose].

=Options=
"""

###############################################################################
#
def processOptions():
    parser = argparse.ArgumentParser(
        description=descr,
        formatter_class=MarkupHelpFormatter
    )
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--showPython",       action='store_true', default=True,
        help='Also show info about which Python will run.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    parser.add_argument(
        'packages',           type=str,
        nargs=argparse.REMAINDER,
        help='Package nam(s)')

    args0 = parser.parse_args()
    return(args0)

def tracePackage(packageName):
    # BASIC PYTHONPATH
    dirs = os.environ['PYTHONPATH'].split(':')
    print("PYTHONPATH:")
    for i, theDir in enumerate(dirs):
        msg = "%2d: '%s'" % (i, theDir)
        if (not os.path.isdir(theDir)): msg += " (NO SUCH DIRECTORY)"
        print(msg)
        if (os.path.isfile(packageName+".py")):
            print("        Found")

    usualWay('port', packageName)
    usualWay('brew', packageName)
    usualWay('brew cask', packageName)
    usualWay('pip', packageName)
    usualWay('conda', packageName)

def usualWay(mgr, packageName):
    print("\n======= %s" % (mgr))
    try:
        cmd = '%s list | grep "%s"' % (mgr, packageName)
        print(check_output(cmd, shell=True))
    except Exception:
        print("*** Failed: %s" % (cmd))


###############################################################################
# Main
#
args = processOptions()

nChecked = 0
if (args.showPython):
    sc = "type python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    sc = "which python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    sc = "whereis python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

if (len(args.packages) == 0):
    sys.stderr.write("No packages specified....\n")
    sys.exit()
else:
    for pkg in (args.packages):
        nChecked += 1
        tracePackage(pkg)

if (not args.quiet):
    print("Done, %d packages checked." % (nChecked))
