#!/usr/bin/env python
#
# mapPHP.py
#
# 2016-03-15: Written. Copyright by Steven J. DeRose.
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
#import subprocess
import codecs

#import pudb
#pudb.set_trace()

from sjdUtils import sjdUtils
from MarkupHelpFormatter import MarkupHelpFormatter

global args, su, lg

__version__ = "2016-03-15"
__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2016-03-15",
    'language'     : "Python 2.7.6",
    'version_date' : "2016-03-15",
    'src_date'     : "$LastChangedDate$",
    'src_version'  : "$Revision$",
}

###############################################################################
#
def processOptions():
    global args, su, lg
    parser = argparse.ArgumentParser(
        description="""

=head1 Description

=head1 Related Commands

=head1 Known bugs and Limitations

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
        "--tickInterval",     type=int, metavar='N', default=10000,
        help='Report progress every n records.')
    parser.add_argument(
        "--unicode",          action='store_const',  dest='iencoding',
        const='utf8', help='Assume utf-8 for input files.')
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
#
def tryOneItem(path):
    """Try to open a file (or directory, if -r is set).
    """
    lg.hMsg(1, "Starting item '%s'" % (path))
    recnum = 0
    if (not os.path.exists(path)):
        lg.error("Couldn't find '%s'." % (path), stat="cantOpen")
    elif (os.path.isdir(path)):
        lg.bumpStat("totalDirs")
        if (args.recursive):
            for child in os.listdir(path):
                recnum += tryOneItem(os.path.join(path,child))
        else:
            lg.vMsg(0, "Skipping directory '%s'." % (path))
    else:
        doOneFile(path)
    return(recnum)


###############################################################################
#
def doOneFile(path):
    """Read and deal with one individual file.
    """
    try:
        fh = open(path, mode="r")  # binary
    except:
        lg.error("Couldn't open '%s'." % (path), stat="cantOpen")
        return(0)
    lg.bumpStat("totalFiles")

    recnum = 0
    rec = ""
    try:
        fh = codecs.open(path, mode='r', encoding=args.iencoding)
    except IOError as e:
        lg.error("Can't open '%s'." % (path), stat="CantOpen")
        return(0)
    while (True):
        try:
            rec = fh.readline()
        except Exception as e:
            lg.error("Error (%s) reading record %d of '%s'." %
                (type(e), recnum, path), stat="readError")
            break
        if (len(rec) == 0): break # EOF
        recnum += 1
        if (args.tickInterval and (recnum % args.tickInterval==0)):
            lg.vMsg(0, "Processing record %d." % (recnum))
        rec = rec.rstrip()
        if (re.match(r'\s*$',rec)):                    # Blank record
            continue
        ###
        # Per-record processing goes here
        ###
        print(rec)
    fh.close()
    return(recnum)


###############################################################################
###############################################################################
# Main
#
args = processOptions()

if (len(args.files) == 0):
    lg.error("No files specified....")
    sys.exit()

for f in (args.files):
    lg.bumpStat("totalFiles")
    recs = doOneFile(f)
    lg.bumpStat("totalRecords", amount=recs)

if (not args.quiet):
    lg.vMsg(0,"Done.")
    lg.showStats()
