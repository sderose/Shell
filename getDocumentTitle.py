#!/usr/bin/env python
#
# getDocumentTitle.py
#
# 2016-07-21: Written. Copyright by Steven J. DeRose.
# 2018-047-18: lint.
#
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
#import codecs

#import pudb
#pudb.set_trace()

#from sjdUtils import sjdUtils
from alogging import ALogger
from MarkupHelpFormatter import MarkupHelpFormatter

#global args, su, lg
lg = ALogger(1)

__version__ = "2018-04-18"
__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2016-07-21",
    'language'     : "Python 2.7.6",
    'version_date' : "2016-07-21",
    'src_date'     : "$LastChangedDate$",
    'src_version'  : "$Revision$",
}

###############################################################################
#
def processOptions():
    parser = argparse.ArgumentParser(
        description="""
=head1 Description

Try to extract the main title from a document(s). This depends on the file type.

For example:

=over

=item * HTML:  Look to "title" or the first "h1" element.

=item * TXT:    Grab the first line?

=item * POD:    The first =h1

=item * PDF:

=item *

=back


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
        "--iencoding",        type=str, metavar='E', default="utf-8",
        help='Assume this character set for input files. Default: utf-8.')
    parser.add_argument(
        "--oencoding",        type=str, metavar='E',
        help='Use this character set for output files.')
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
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
    if (args0.verbose): lg.setVerbose(args0.verbose)
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
    t = ""
    (root, ext) = os.path.splitext(path)
    if (ext == 'html' or ext == 'htm'):
        cmd = "grep '<(title|h1).*?((</(title|h1)>|$)' '%s'" % (path)
        t = subprocess.check_output(cmd)
    elif (ext == 'pdf'):
        cmd = "pdfinfo '%s' | grep -max 1 '^(Author|Title):'" % (path)
        t = subprocess.check_output(cmd)
        # Or pdftohtml -i -stdout -xml -nodrm -f 1 -l 5
        # Cf http://csxstatic.ist.psu.edu/about/scholarly-information-extraction
    elif (ext == 'txt'):
        # head -n 1
        pass
    elif (ext == 'pod' or ext == 'pl'):
        cmd = "grep '^=h1' '%s'" % (path)
        t = subprocess.check_output(cmd)
    elif (ext == 'xml'):
        pass
    return(t)


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
