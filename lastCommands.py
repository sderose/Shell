#!/usr/bin/env python3
#
# lastCommands.py: Re-un the last N commands from the shell history.
# 2014-06-19: Written by Steven J. DeRose.
#
import sys
import os
import re
import codecs
from subprocess import check_output

__metadata__ = {
    "title"        : "lastCommands",
    "description"  : "Re-un the last N commands from the shell history.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2014-06-19",
    "modified"     : "2021-02-23",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]


descr = """
=Usage=

Extract and execute the last N bash commands. This should be invoked via
a shell function that saves the history somewhere, and then passes the
path to it. Otherwise it's hard to get the truly up-to-date history.


=Related Commands=

=Known bugs and Limitations=

This can't change state of the calling shell, such as environment variables.


=History=

  * 2014-06-19: Written by Steven J. DeRose.
  * 2021-02-23: New layout. Default to asking shell for history.


=Rights=

Copyright 2014-06-19 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
For further information on this license, see
[https://creativecommons.org/licenses/by-sa/3.0].

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].
=Options=
"""


###############################################################################
# Main
#
if __name__ == "__main__":
    import argparse

    def processOptions():
        try:
            from BlockFormatter import BlockFormatter
            parser = argparse.ArgumentParser(
                description=descr, formatter_class=BlockFormatter)
        except ImportError:
            parser = argparse.ArgumentParser(description=descr)

        parser = argparse.ArgumentParser(
            description=descr)
        parser.add_argument(
            "--histfile", type=str,
            help="What history file to use.")
        parser.add_argument(
            "--quiet", "-q", action="store_true", dest="quiet",
            help="Suppress most messages.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version="Version of "+__version__,
            help="Display version information, then exit.")

        parser.add_argument(
            "n", type=int,
            help="How many commands to re-do.")

        args0 = parser.parse_args()
        return args0


    args = processOptions()

    ignoreList = [
        "lastCommands", "lastCommands.py"
    ]

    if (args.histfile):
        with codecs.open(args.histfile, "rb", encoding="utf-8") as ifh:
            hist = ifh.read()
    else:
        hist = check_output("history %d" % (args.n), shell=True)

    todo = []
    while (True):
        rec = hist.split().strip()
        if (rec == ""): break
        if (len(todo) >= args.n): todo.pop()
        rec = re.sub(r"^\s*\d+\s+","",rec)
        cmd = re.sub(r"\s.*","",rec)
        if (cmd not in ignoreList): todo.append(rec)

    if (args.verbose):
        sys.stderr.write("\n".join(todo) + "\n")

    for c in (todo):
        if (True or args.verbose):
            sys.stderr.write("\nRunning: %s\n" % (c))
        os.system(c)

    if (args.verbose):
        sys.stderr.write("\nlastCommand.py: %d one.\n" % (args.n))
