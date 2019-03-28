#!/usr/bin/env python
#
# spinner.py: Show a spinning clock or something.
#
# 2018-03-24: Written. Copyright by Steven J. DeRose.
# Creative Commons Attribution-Share-alike 3.0 unported license.
# See http://creativecommons.org/licenses/by-sa/3.0/.
# 2018-11-07: Py 3.
#
# To do:
#
from __future__ import print_function
import sys, os
import argparse

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    #import HTMLParser
    string_types = basestring
else:
    #from html.parser import HTMLParser
    string_types = str
    def unichr(n): return chr(n)

__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2018-03-24",
    'language'     : "Python 2.7.6",
    'version_date' : "2018-11-07",
}
__version__ = __metadata__['version_date']


###############################################################################
#
def processOptions():
    descr = """

=head1 Description

Display a spinning clock-face in a shell window using Unicode clock-faces.

=head1 Related Commands

=head1 Known bugs and Limitations

=head1 Licensing

Copyright 2015 by Steven J. DeRose. This script is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See http://creativecommons.org/licenses/by-sa/3.0/ for more information.

=head1 Options
        """

    try:
        from MarkupHelpFormatter import MarkupHelpFormatter
        formatter = MarkupHelpFormatter
    except ImportError:
        formatter = None
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=formatter)

    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    args0 = parser.parse_args()
    return(args0)


###############################################################################
###############################################################################
# Main
#
args = processOptions()

clockMin = 0x1F550
clockMax = 0x1F55B

cur = clockMax
while(1):
    cur += 1
    if (cur>clockMax): cur = clockMin
    u = unichr(cur)
    #u = eval('u"\U%08x"' % (cur))  # unichr(cur)
    print(u + chr(8), end="")
    #sleep(1)

