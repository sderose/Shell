#!/usr/bin/env python
#
# countShells.py
#
from __future__ import print_function
import sys, os, argparse
import pwd
import re
import math
from subprocess import check_output
from collections import namedtuple

from MarkupHelpFormatter import MarkupHelpFormatter

__metadata__ = {
    'title'        : "countShells.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2017-02-03",
    'modified'     : "2020-03-01",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Description=

Show how many bash shells are running for the current user.

''Unfinished''

The count depends on definitions:

* Just bash, or any shell?

* Just login shells?

* Foreground and/or background?

* Attached to a terminal?

=Related Commands=

`w`, `last`, `ps`,....

=Known bugs and Limitations=

BSD support is experimental.

=History=

* 2017-02-03: Written. Copyright by Steven J. DeRose.

=Rights=

Copyright 2017 by Steven J. DeRose. This work is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see [http://creativecommons.org/licenses/by-sa/3.0].

For the most recent version, see [http://www.derose.net/steve/utilities] or
[http://github.com/sderose].

=Options=
"""

###############################################################################
#
def processOptions():
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=MarkupHelpFormatter
    )
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--shellName",        type=str, default='bash',
        help='What shell program to check for. Default: bash.')
    parser.add_argument(
        "--verbose", "-v",    action='count', default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version",          action='version', version=__version__,
        help='Display version information, then exit.')

    parser.add_argument(
        'files',              type=str,
        nargs=argparse.REMAINDER,
        help='Path(s) to input file(s)')

    args0 = parser.parse_args()
    return(args0)


###############################################################################
#
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
    second = s % 60
    minute = math.floor(s/60) % 60
    hour = math.floor(s/3600)
    return("%02s:%02s:%02s" % (second, minute, hour))


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
            print("Missing header?")
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
