#!/usr/bin/env python
#
# genKey.py
#
# 2016-01-04: Written. Copyright by Steven J. DeRose.
# Creative Commons Attribution-Share-alike 3.0 unported license.
# See http://creativecommons.org/licenses/by-sa/3.0/.
#
# To do:
#
from __future__ import print_function
import sys, os, argparse
#import re
import string
#import math
#import subprocess
import codecs
import random

#import pudb
#pudb.set_trace()

from sjdUtils import sjdUtils
from MarkupHelpFormatter import MarkupHelpFormatter

global args, su, lg
args = None

__version__ = "2016-01-04"
__metadata__ = {
    'creator'      : "Steven J. DeRose",
    'cre_date'     : "2016-01-04",
    'language'     : "Python 2.7.6",
    'version_date' : "2016-01-04",
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

Generate a random key, from a given set of symbols and of a given length.

=head2 Notes

Use I<--symbols S> to choose what symbols to draw from:

=over

=item 'ascii' only includes printable characters.

=item 'alpha', 'upper', 'lower', 'alphanum', and 'digits' only draw from ASCII.

=item 'latin1' uses 'ascii' plus I<letters> from the upper half.

=item 'utf8' uses string.printable, and so may depend on locale.

=item 'hex' only includes uppercase versions of A-F.

=item Characters are drawn with uniform probability (thus, letters are no more
likely than digits or punctuation with 'alphanum', etc.).

=item Words are drawn from a file that should contain one word per line.
The default file is F</usr/share/dict/words> (but see I<--dict>).

=back

=head1 Related Commands

C<randomRecords>, C<gendsa>, C<genpkey>, C<genrsa>, C<openssl rand>.

=head1 Known bugs and Limitations

Randomness of the key is whatever Python supplies. This may or may not
be good enough for your needs.

=head1 Licensing

Copyright 2015 by Steven J. DeRose. This script is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See http://creativecommons.org/licenses/by-sa/3.0/ for more information.

=head1 Options
        """,
        formatter_class=MarkupHelpFormatter
    )
    parser.add_argument(
        "--dict",             type=str, default='/usr/share/dict/words',
        help='A dictionary file to use with --symbols words.')
    parser.add_argument(
        "--length", "-n",     type=int, default=12, metavar='N',
        help='length of key.')
    parser.add_argument(
        "--punc",             type=str, default='._!@*~?',
        help='Which punctuation to allow.')
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--seed",             type=int,
        help='Seed for random-number generator.')
    parser.add_argument(
        "--symbols",          type=str, default="alphanum",
        choices=[ 'ascii', 'latin1', 'alpha', 'upper', 'lower',
            'alphanum', 'digits', 'hex', 'utf8', 'words' ],
        help='Which possible set of symbols to draw from.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    args0 = parser.parse_args()
    su = sjdUtils()
    lg = su.lg
    su.setVerbose(args0.verbose)
    return(args0)


###############################################################################
# Main
#
args = processOptions()
if (args.seed): random.seed(args.seed)

symbolSet = None
if (args.symbols == 'alpha'):
    symbolSet = string.ascii_letters
elif (args.symbols == 'upper'):
    symbolSet = string.ascii_uppercase
elif (args.symbols == 'lower'):
    symbolSet = string.ascii_lowercase
elif (args.symbols == 'alphanum'):
    symbolSet = string.ascii_letters + string.digits
elif (args.symbols == 'digits'):
    symbolSet = string.digits
elif (args.symbols == 'hex'):
    symbolSet = string.digits + 'ABCDEF'  # Only one case!
elif (args.symbols == 'ascii'):
    symbolSet = string.ascii_letters + string.digits + string.punctuation
elif (args.symbols == 'latin1'):
    symbolSet = string.ascii_letters + string.digits + string.punctuation
    for i in range(161, 255):   # No Yen / DEL, please.
        c = unichr(i)
        if (c.isalpha()): symbolSet += c
elif (args.symbols == 'utf8'):
    symbolSet = string.printable
elif (args.symbols == 'words'):
    symbolSet = open(args.dict, 'r').read().split()
else:
    print("Unknown symbol set '%s'." % (args.symbols))
    sys.exit()
symbolSetLength = len(symbolSet)

key = ""
for f in (range(args.length)):
    key += symbolSet[random.randint(0, symbolSetLength)]
    if (args.symbols == 'words'):
        key += ' '
print(key)
