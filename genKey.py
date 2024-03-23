#!/usr/bin/env python3
#
# genKey.py: Generate a random key from given symbols and length.
# 2016-01-04: Written by Steven J. DeRose.
#
import sys
import argparse
import string
import random
import codecs

__metadata__ = {
    "title"        : "genKey",
    "description"  : "Generate a random key from given symbols and length.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2016-01-04",
    "modified"     : "2020-03-01",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
=Description=

Generate a random key, from a given set of symbols and of a given length.

==Notes==

Use '--symbols S' to choose what symbols to draw from:

* 'ascii' only includes printable characters.

* 'alpha', 'upper', 'lower', 'alphanum', and 'digits' only draw from ASCII.

* 'latin1' uses 'ascii' plus 'letters' from the upper half.

* 'utf8' uses string.printable, and so may depend on locale.

* 'hex' only includes uppercase versions of A-F.

* Characters are drawn with uniform probability (thus, letters are no more
likely than digits or punctuation with 'alphanum', etc.).

* Words are drawn from a file that should contain one word per line.
The default file is F</usr/share/dict/words> (but see '--dict').


=Related Commands=

`randomRecords`, `gendsa`, `genpkey`, `genrsa`, `openssl rand`.

=Known bugs and Limitations=

Randomness of the key is whatever Python supplies. This may or may not
be good enough for your needs.


=Rights=

Copyright 2016-01-04 by Steven J. DeRose.
This work is licensed under a Creative Commons
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
        "--dencoding", type=str, metavar='E', default="utf-8",
        help='Assume this character set for dictionary files. Default: utf-8.')
    parser.add_argument(
        "--dict", type=str, default='/usr/share/dict/words',
        help='A dictionary file to use with --symbols words.')
    parser.add_argument(
        "--length", "-n", type=int, default=12, metavar='N',
        help='length of key.')
    parser.add_argument(
        "--punc", type=str, default='._!@*~?',
        help='Which punctuation to allow.')
    parser.add_argument(
        "--quiet", "-q", action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--seed", type=int,
        help='Seed for random-number generator.')
    parser.add_argument(
        "--symbols", type=str, default="alphanum",
        choices=[ 'ascii', 'latin1', 'alpha', 'upper', 'lower',
            'alphanum', 'digits', 'hex', 'utf8', 'words' ],
        help='Which possible set of symbols to draw from.')
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
        c = chr(i)
        if (c.isalpha()): symbolSet += c
elif (args.symbols == 'utf8'):
    symbolSet = string.printable
elif (args.symbols == 'words'):
    dfh = codecs.open(args.dict, 'rw', encoding=args.dencoding)
    symbolSet = dfh.read().split()
    dfh.close()
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
