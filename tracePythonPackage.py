#!/usr/bin/env python
#
# tracePythonPackage.py: Find where a Python package is installed.
# 2018-05-18: Written by Steven J. DeRose.
#
from __future__ import print_function
import sys, os
import argparse
import re
import subprocess
from subprocess import check_output

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

__metadata__ = {
    'title'        : "tracePythonPackage.py",
    'description'  : "Find where a Python package is installed.",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2018-05-18",
    'modified'     : "2020-10-07",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Description=

See where Python is getting a given package
(packages whose name ''contains'' the requested string are also reported).

Python package managers included:

    PYTHONPATH itself (via sys.path)
    pip
    port
    conda
    brew
    apt

'''Note''': A package manager's name for something, is often not the same as the
name you import. For example, you would import "sklearn", but it lives in
a package called "scikit-learn" (which you cannot import, but only install).

This command does not know about `PyPM`, `EasyInstall`, `Virtualenv`,
or the meta-manager `pyenv`.

Apparently Python will only resolve `import pkg` if:

* pkg does *not* include the ".py" extension

* the file *does* have extension ".py" (not even ".pyc")

* the file is not in a subdirectory of the PYTHONPATH dir specified
(and you can't specify the path in the import statement, either).


=Related Commands=

`pipdeptree` -- finds all the dependency chains and version ranges known for
installed pip libraries.

`pipcompile` [https://github.com/jazzband/pip-tools] -- creates a
requirements.txt file. See
[https://medium.com/knerd/the-nine-circles-of-python-dependency-hell-481d53e3e025]

My `identifyAllExecutables` -- search `PATH` for executables of a given name,
as well as reporting shell functions, aliases,shell keywords, and builtins.


=Known bugs and Limitations=

Probably should also be able to list the versions of the package managers.


=History=

  2018-05-18: Written by Steven J. DeRose.
  2020-10-07: Use `sys.path`, make `PYTHONPATH` optional. Trap `grep` fail.


=Rights=

Copyright 2018-05-18 by Steven J. DeRose.
This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[https://github.com/sderose].

=Options=
"""


###############################################################################
#
def tracePackage(packageName):
    # BASIC PYTHONPATH
    if (args.pythonpath):
        dirs = os.environ['PYTHONPATH'].split(sep=':')
        print("\n======= PYTHONPATH:")
        checkDirs(dirs, packageName)

    print("\n======= current sys.path:")
    checkDirs(sys.path, packageName)

    usualWay('port list', packageName)
    usualWay('brew list --formula', packageName)
    usualWay('brew list --cask', packageName)
    usualWay('pip list', packageName)              ## or pip show [x]
    usualWay('conda list', packageName)
    usualWay('apt list', packageName)


def checkDirs(dirs, packageName):
    for i, theDir in enumerate(dirs):
        msg = "%2d: '%s'" % (i, theDir)
        if (not os.path.isdir(theDir)): msg += " (NO SUCH DIRECTORY)"
        if (not args.quiet): print(msg)
        if (os.path.isfile(packageName+".py")):
            print("        *** Found ***")

def usualWay(mgr, packageName):
    print("\n======= Checking %s" % (mgr))
    try:
        cmd = '%s | grep "%s"' % (mgr, packageName)
        print(check_output(cmd, shell=True))
    except subprocess.CalledProcessError as e:
        if (re.search(r'returned non-zero exit status 1', "%s" % (e))):
            pass  # Normal grep 'not found'
        else:
            print("*** Failed: %s:\n    %s" % (cmd, e))


###############################################################################
#
def processOptions():
    try:
        from BlockFormatter import BlockFormatter
        parser = argparse.ArgumentParser(
            description=descr, formatter_class=BlockFormatter)
    except ImportError:
        parser = argparse.ArgumentParser(description=descr)

    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--pythonpath",       action='store_true',
        help='Check along PYTHONPATH, not just sys.path.')
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
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--pythonpath",       action='store_true',
        help='Check along PYTHONPATH, not just sys.path.')
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


args = processOptions()

nChecked = 0
if (args.showPython):
    sc = "type python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    sc = "which python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    sc = "whereis python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    print("======= Running Python: %s" + str(sys.version_info))

if (len(args.packages) == 0):
    sys.stderr.write("No packages specified....\n")
    sys.exit()
else:
    for pkg in (args.packages):
        nChecked += 1
        tracePackage(pkg)

if (not args.quiet):
    print("Done, checked for %d package(s)." % (nChecked))
