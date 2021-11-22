#!/usr/bin/env python
#
# spinner.py: Show a spinning clock or something.
# 2018-03-24: Written by Steven J. DeRose.
#
from __future__ import print_function
import sys
import argparse

PY3 = sys.version_info[0] == 3
if PY3:
    def unichr(n): return chr(n)

__metadata__ = {
    'title'        : "spinner.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2018-03-24",
    'modified'     : "2020-03-01",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """

=Description=

Display a spinning clock-face in a shell window using Unicode clock-faces.


=Related Commands=


=Known bugs and Limitations=


=History=

* 2018-03-24: Written by Steven J. DeRose.
* 2018-11-07: Py 3.


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
def processOptions():
    try:
        from BlockFormatter import BlockFormatter
        parser = argparse.ArgumentParser(
            description=descr, formatter_class=BlockFormatter)
    except ImportError:
        parser = argparse.ArgumentParser(description=descr)

    parser.add_argument(
        "--quiet", "-q", action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--verbose", "-v", action='count', default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    args0 = parser.parse_args()
    return(args0)


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
