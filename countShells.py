#!/usr/bin/env python
#
# countShells.py
#
# 2017-02-03: Written. Copyright by Steven J. DeRose.
# Creative Commons Attribution-Share-alike 3.0 unported license.
# See http://creativecommons.org/licenses/by-sa/3.0/.
#
# To do:
#
from __future__ import print_function
import sys, os, argparse
import pwd
import re
#import string
#import math
from subprocess import check_output
from collections import namedtuple

from sjdUtils import sjdUtils
from MarkupHelpFormatter import MarkupHelpFormatter

global args, su, lg

__version__ = "2017-02-03"
__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2017-02-03",
    'language'     : "Python 2.7.6",
    'version_date' : "2017-02-03",
}

###############################################################################
#
def processOptions():
    global args, su, lg
    parser = argparse.ArgumentParser(
        description="""

=head1 Description

Show how many bash shells are running for the current user."

The count depends on definitions:

=over

=item * Just bash, or any shell?

=item * Just login shells?

=item * Foreground and/or background?

=item * Attached to a terminal?

=back

=head1 Related Commands

w, last, ps,...

=head1 Known bugs and Limitations

BSD support is experimental.

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
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--shellName",        type=str, default='bash',
        help='What shell program to check for. Default: bash.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    parser.add_argument(
        'files',             type=str,
        nargs=argparse.REMAINDER,
        help='Path(s) to input file(s)')

    args0 = parser.parse_args()
    su = sjdUtils()
    lg = su.getLogger()
    lg.setVerbose(args0.verbose)
    if (args0.color == None):
        args0.color = ("USE_COLOR" in os.environ and sys.stderr.isatty())
    su.setColors(args0.color)
    return(args0)


###############################################################################
linuxStateCodes = {
    'D': 'uninterruptible sleep (usually IO)',
    'R': 'running or runnable (on run queue)',
    'S': 'interruptible sleep (waiting for an event to complete)',
    'T': 'stopped, either by a job control signal or because it is being traced',
    'W': 'paging (not valid since the 2.6.xx kernel)',
    'X': 'dead (should never be seen)',
    'Z': 'defunct ("zombie") process, terminated but not reaped by its parent',

      # For BSD formats and when the stat keyword is used, additional
      # characters may be displayed:

    '<': 'high-priority (not nice to other users)',
    'N': 'low-priority (nice to other users)',
    'L': 'has pages locked into memory (for real-time and custom IO)',
    's': 'is a session leader',
    'l': 'is multi-threaded (using CLONE_THREAD, like NPTL pthreads do)',
    '+': 'is in the foreground process group',
}


def formatSecond(s):
    sec = s % 60
    min = floor(s/60) % 60
    hour = floor(s/3600)
    return("%02s:%02s:%02s" % (sec, min, hour))

###############################################################################
###############################################################################
# Main
#
# @see psTest.py for info in Linux vs. BSD options.
#
args = processOptions()

### etimes not on bsd, though etime is....
### But etime does not seem to work on Linux, though man says it should.
###
fieldList = [ 'user', 'start', 'etimes', 'stat', 'comm' ]
PSInfo = namedtuple('PSInfo', fieldList, verbose=False)

#if (args.verbose):
#    print("$OSTYPE appears to be: '%s'." % (os.environ['OSTYPE']))

print("WARNING: ps flaky. See psText.")

user = os.environ['USER']

formatArg = ' '.join(fieldList)
info = check_output(['ps', '-u', user, '-o', formatArg ])
recnum = 0
ignored = 0
for x in info.splitlines():
    recnum += 1
    if (recnum==1):
        if (not re.match(r'^[ A-Z%]+$', x)):
            print("Missing header?");
            sys.exit()
        headerTokens = re.split(r'\s+', x)
        if (len(headerTokens) != len(fieldList)):
            print("Header (%d) vs. fieldList (%d) mismatch!\n    %s" %
                  (len(headerTokens), len(fieldList), ", ".join(headerTokens)))
        if (args.verbose): print("Header ok, %d fields." % (len(fieldList)))
        continue

    x = x.strip()
    tokens = re.split(r'\s+', x, maxsplit=len(fieldList)-1)
    # We'll only catch if there are too FEW (extras would emd up in 'command')
    if (len(tokens) == len(fieldList)):
        tup = PSInfo._make(tokens)
    else:
        print("Bad token count (%d, not %d) from:\n  %s\n  %s" %
                (len(tokens), len(fieldList), x, ';'.join(tokens)))
        sys.exit()

    # Convert numeric userid to name, if needed
    try:
        u = tokens[0] - 1
        tokens[0] = pwd.getpwuid(os.getuid()).pw_name
    except TypeError:  # was already non-numeric
        pass

    tup = PSInfo._make(tokens)
    if (args.shellName and not re.match(r'\W*'+args.shellName, tup.comm)):
        ignored += 1
        continue

    if (args.verbose): 
        print("*** Process ***\n    '%s'" % (x))
        for k, v in tup._asdict().items():
            print("    %-8s  %s" % (k,v))
    delta = formatSecond(tup.etimes)

if (args.verbose):
    print("Processes ignored (vs. '%s'): %d." % (args.shellName, ignored))
