#!/usr/bin/env python
#
# lastCommands.py
#
# 2014-06-19: Written by Steven J. DeRose.
#
from __future__ import print_function
import sys
import os
import re
import argparse

__metadata__ = {
    'title'        : "ColorManager.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2014-06-19",
    'modified'     : "2020-03-01",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Usage=

Extract and execute the last N bash commands. This should be invoked via
a shell function that saves the history somewhere, and then passes the
path to it. Otherwise it's hard to get the truly up-to-date history.

This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see L<http://creativecommons.org/licenses/by-sa/3.0/>.

For the most recent version, see L<http://www.derose.net/steve/utilities/>.

=Rights=

This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[http://github.com/sderose].

=Options=
"""

###############################################################################
# Process options
#
parser = argparse.ArgumentParser(
    description=descr)
parser.add_argument(
    "n",                 type=int,
    help='How many commands to re-do.')
parser.add_argument(
    "--quiet", "-q",     action='store_true', dest='quiet',
    help='Suppress most messages.')
parser.add_argument(
    "--verbose", "-v",   action='count', default=0,
    help='Add more messages (repeatable).')
parser.add_argument(
    "--version",         action='version', version='Version of '+__version__,
    help='Display version information, then exit.')
parser.add_argument(
    "histfile",                 type=str,
    help='What history file to use.')

args = parser.parse_args()

ignoreList = [
    "lastCommands", "lastCommands.py"
]


###############################################################################
###############################################################################
# Main
#
ifh = open(args.histfile, 'r')
if (not ifh):
    sys.stderr.write("Can't open history file from '%s'." % (args.histfile))
    sys.exit()

todo = []
while (True):
    rec = ifh.readline().strip()
    if (rec == ''): break
    if (len(todo) >= args.n): todo.pop()
    rec = re.sub(r'^\s*\d+\s+','',rec)
    cmd = re.sub(r'\s.*','',rec)
    if (cmd not in ignoreList): todo.append(rec)

if (args.verbose):
    sys.stderr.write("\n".join(todo) + "\n")

for c in (todo):
    if (True or args.verbose):
        sys.stderr.write("\nRunning: %s\n" % (c))
    os.system(c)

if (args.verbose):
    sys.stderr.write("\nlastCommand.py: %d one.\n" % (args.n))

sys.exit(0)

