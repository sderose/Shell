#!/usr/bin/env python
#
# packageHelper.py
#
# 2015-09-18: Written. Copyright by Steven J. DeRose.
# Creative Commons Attribution-Share-alike 3.0 unported license.
# See http://creativecommons.org/licenses/by-sa/3.0/.
#
# To do:
#
from __future__ import print_function
import sys, os, argparse
#import re
#import string
#import math
import subprocess
import codecs

#import pudb
#pudb.set_trace()

from sjdUtils import sjdUtils
#from alogging import ALogger
from MarkupHelpFormatter import MarkupHelpFormatter

global args, su, lg
su = lg = None
#lg = ALogger(1)

#
__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2015-09-18",
    'language'     : "Python 2.7.6",
    '__version__' : "2015-09-18",
    'src_date'     : "$LastChangedDate$",
    'src_version'  : "$Revision$",
}

###############################################################################
#
def processOptions():
    global args, su
    parser = argparse.ArgumentParser(
        description="""

=head1 Description

Find out which stuff has been installed by which package managers.

This script only tries to deal with Mac OS X and Ubuntu.

=head2 List of some package managers

See L<Wikipedia|"https://en.wikipedia.org/wiki/List_of_software_package_management_systems">

Mac:
    Homebrew
    MacPorts (nee DarwinPorts, based os FreeBSD Ports)
    easy_install
    fink
    rudix
    Joyent (based on pksrc)
    Nix

Linux:
    dpkg / apt-get (Debian, Ubuntu)
    RPM (RedHat et al)
    linuxbrew (cf Mac Homebrew)
    Pacman (Arch, Frugalware, DeLi)
    tgz (Slackware)
    Smart Package Manager (CCux)
    ipkg (cf dpkg; HP webOS)
    opkg (fork of ipkg)
    pkgutils (CRUX)
    PETget (Puppy)
    Upkg (paldo GNU/Linux)
    PISI (Pardus)
    Conary (Foresight)
    Equo (Sabayon)
    Tazpkg (Slitaz)
    eopkg (Solus)
    xbps (Void)

Language-specific:
    Python: pip Anaconda EasyInstall (<Setuptools)
    Perl: cpan
    R: CRAN
    T: CTAN
    Ruby: RubyGems, Bundler
    Java: Maven

=head1 Related Commands

C<pythonpath>, C<identifyAllExecutables>

=head1 Known bugs and Limitations

Incomplete.

=head1 Licensing

Copyright 2015 by Steven J. DeRose. This script is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See http://creativecommons.org/licenses/by-sa/3.0/ for more information.

=head1 Options
        """,
        formatter_class=MarkupHelpFormatter
    )
    parser.add_argument(
        "--color",  # Don't default. See below.
        help='Colorize the output.')
    parser.add_argument(
        "--extension",        type=str, metavar='E', default="",
        help='Only process input files with this extension. Default: "" (=all).')
    parser.add_argument(
        "--iencoding",        type=str, metavar='E', default="utf-8",
        help='Assume this character set for input files. Default: utf-8.')
    parser.add_argument(
        "--ignoreCase", "-i", action='store_true',
        help='Disregard case distinctions.')
    parser.add_argument(
        "--oencoding",        type=str, metavar='E',
        help='Use this character set for output files.')
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--recursive",        action='store_true',
        help='Traverse subdirectories.')
    parser.add_argument(
        "--tickInterval",     type=int, metavar='N', default=10000,
        help='Report progress every n records.')
    parser.add_argument(
        "--unicode",          action='store_const',  dest='iencoding',
        const='utf8', help='Assume utf-8 for input files.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__metadata__['__version__'],
        help='Display version information, then exit.')

    parser.add_argument(
        'files',             type=str,
        nargs=argparse.REMAINDER,
        help='Path(s) to input file(s)')

    args0 = parser.parse_args()
    su = sjdUtils()
    su.setVerbose(args0.verbose)
    if (args0.color is None):
        args0.color = ("USE_COLOR" in os.environ and sys.stderr.isatty())
    su.setColors(args0.color)
    return(args0)


###############################################################################
###############################################################################
# Main
#
args = processOptions()

su.lg.hMsg(0, "Unfinished")

ports = subprocess.check_output(['port list installed'])
brews = subprocess.check_output(['brew search'])
pips  = subprocess.check_output(['pip list installed'])
anacondas = ''
#finks =subprocess.check_output([''])

if (not args.quiet): lg.vMsg(0,"Done.")
if (args.verbose): su.showStats()
