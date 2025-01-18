#!/usr/bin/env python3
#
# getDocumentTitle.py: Rudimentary document-title finder.
# 2016-07-21: Written by Steven J. DeRose.
#
import sys
import os
import argparse
import subprocess
import logging

lg = logging.getLogger("getDocumentTitle")

__metadata__ = {
    "title"        : "getDocumentTitle",
    "description"  : "Rudimentary document-title finder.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2016-07-21",
    "modified"     : "2020-03-04",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']


descr = """
=Description=

Try to extract the main title from a document(s). This depends on the file type.

For example:

* HTML:  Look to "title" or the first "h1" element.

* TXT:    Grab the first line?

* POD:    The first =h1

* MarkDown: The first =.*=

* PDF:


=Related Commands=


=Known bugs and Limitations=


=History=

* 2016-07-21: Written by Steven J. DeRose.
* 2018-047-18: lint.
* 2020-03-04: lint, new layout, POD to MarkDown.


=Rights=

This work by Steven J. DeRose is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[http://github.com/sderose].


=Options=
"""


###############################################################################
#
def tryOneItem(path):
    """Try to open a file (or directory, if -r is set).
    """
    lg.log(logging.INFO-1, "====Starting item '%s'", path)
    recnum = 0
    if (not os.path.exists(path)):
        lg.error("Couldn't find '%s'.", path)
    elif (os.path.isdir(path)):
        lg.bumpStat("totalDirs")
        if (args.recursive):
            for child in os.listdir(path):
                recnum += tryOneItem(os.path.join(path,child))
        else:
            lg.info("Skipping directory '%s'.", path)
    else:
        doOneFile(path)
    return(recnum)


###############################################################################
#
def doOneFile(path):
    """Read and deal with one individual file.
    """
    t = ""
    (_root, ext) = os.path.splitext(path)
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
        "--iencoding", type=str, metavar='E', default="utf-8",
        help='Assume this character set for input files. Default: utf-8.')
    parser.add_argument(
        "--oencoding", type=str, metavar='E',
        help='Use this character set for output files.')
    parser.add_argument(
        "--quiet", "-q", action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--unicode", action='store_const', dest='iencoding',
        const='utf8', help='Assume utf-8 for input files.')
    parser.add_argument(
        "--verbose", "-v", action='count', default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    parser.add_argument(
        'files', type=str, nargs=argparse.REMAINDER,
        help='Path(s) to input file(s)')

    args0 = parser.parse_args()
    if (lg and args0.verbose):
        logging.basicConfig(level=logging.INFO - args0.verbose,
            format="%(message)s")
    return(args0)

args = processOptions()

if (len(args.files) == 0):
    lg.error("No files specified....")
    sys.exit()

for f in (args.files):
    lg.bumpStat("totalFiles")
    recs = doOneFile(f)
    lg.bumpStat("totalRecords", amount=recs)

if (not args.quiet):
    lg.info("Done.")
