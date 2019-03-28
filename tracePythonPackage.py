#!/usr/bin/env python
#
# tracePythonPackage.py
#
# 2018-05-18: Written. Copyright by Steven J. DeRose.
# Creative Commons Attribution-Share-alike 3.0 unported license.
# See http://creativecommons.org/licenses/by-sa/3.0/.
#
# To do:
#
from __future__ import print_function
import sys, os
import argparse
#import re
from subprocess import check_output

from alogging import ALogger
from MarkupHelpFormatter import MarkupHelpFormatter

__version__ = "2018-05-18"
__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2018-05-18",
    'language'     : "Python 2.7.6",
    'version_date' : "2018-05-18",
}

#su = sjdUtils()
lg = ALogger(1)


###############################################################################
#
def processOptions():
    parser = argparse.ArgumentParser(
        description="""

=head1 Description

Look all over the place to see where Python is getting a given package
(packages whose name I<contains> the requested string are also reported).

Python package managers include:

    PYTHONPATH itself
    pip
    port
    conda
    brew

B<Note>: A package manager's name for something, is often not the same as the
name you import. For example, you would import "sklearn", but it lives in
a package called "scikit-learn" (which you cannot import, but only install).


This command does not know about C<PyPM>, C<EasyInstall>, C<Virtualenv>,
or the meta-manager C<pyenv>.

Apparently Python will only resolve C<import pkg> if:

    * pkg does *not* include the ".py" extension

    * the file *does* have extension ".py" (not even ".pyc")

    * the file cannot be in a subdirectory of the PYTHONPATH dir specified
    (and you can't specify the path in the import statement, either).


=head1 Related Commands

C<identifyAllExecutables> -- search C<PATH> for executables of a given name,
as well as reporting shell functions, aliases,shell keywords, and builtins.

=head1 Known bugs and Limitations

Probably should also be able to list the versions of the package managers.

=head1 Licensing

Copyright 2015 by Steven J. DeRose. This script is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See http://creativecommons.org/licenses/by-sa/3.0/ for more information.

=head1 Options
        """,
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
    if (args0.verbose): lg.setVerbose(args0.verbose)
    return(args0)



def tracePackage(p):
    # BASIC PYTHONPATH
    dirs = os.environ['PYTHONPATH'].split(':')
    lg.info("PYTHONPATH:")
    for i, dir in enumerate(dirs):
        msg = "%2d: '%s'" % (i, dir)
        if (not os.path.isdir(dir)): msg += " (NO SUCH DIRECTORY)"
        lg.info(msg)
        if (os.path.isfile(pkg+".py")):
            lg.info("        Found")

    usualWay('port', p)
    usualWay('brew', p)
    usualWay('brew cask', p)
    usualWay('pip', p)
    usualWay('conda', p)


def usualWay(mgr, p):
    lg.info("\n======= %s" % (mgr))
    try:
        cmd = '%s list | grep "%s"' % (mgr, p)
        print(check_output(cmd, shell=True))
    except Exception as e:
        print("*** Failed: %s" % (cmd))



###############################################################################
###############################################################################
# Main
#
args = processOptions()

if (args.showPython):
    sc = "type python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    sc = "which python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

    sc = "whereis python"
    print("======= %s\n%s" % (sc, check_output(sc, shell=True)))

if (len(args.packages) == 0):
    lg.error("No packages specified....")
    doOneFile("[STDIN]", sys.stdin.readlines)
else:
    for pkg in (args.packages):
        lg.bumpStat("Total Packages checked")
        tracePackage(pkg)

if (not args.quiet):
    lg.vMsg(0,"Done.")
    lg.showStats()
