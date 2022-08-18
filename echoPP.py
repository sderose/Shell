#!/usr/bin/env python3
#
# echoPP.py: Slight improvement on *nix 'echo'.
# 2022-02-25: Written by Steven J. DeRose.
#
import sys
import re
import logging
lg = logging.getLogger()

__metadata__ = {
    "title"        : "echoPP",
    "description"  : "Slight improvement on *nix 'echo'.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2022-02-25",
    "modified"     : "2022-04-07",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Name=
    """ +__metadata__["title"] + ": " + __metadata__["description"] + """


=Description=

Add these features to `echo` (by default, should work just the same as
regular POSIX `echo`):

* Option to write to stderr (--stderr OR -2).
* Basic ANSI colors.
* Set newline string (not just ''-n'' to suppress newlines)
* Input and output encodings (--iencoding, --oencoding).
* Making things visible by escaping non-ASCII, non-Latin-1, controls,
and/or whitespace.
* Option to turn on (or leave off) echo's support for ending the input
with "\\c" to suppress newline
(which POSIX leaves as implementation-defined behavior).

==Usage==

    echoPP.py [options] [text]


=See also=

    `mathAlphanumerics.py`
    `colorString.py`
    `highlight`
    `showInvisibles`


=Known bugs and Limitations=

* Unicode > 0xFFFF doesn't use \\U%08x instead of \\u%04x.


=To do=

* Offer inline emphasis (*word*, _word_, `word`) and/or color?
* Background colors, 256-color, ANSI effects.
* sprintf?
* decode \\xFF, \\uFFFF, \\U, \\x{}, &x;, %ff, etc (--decode)?


=History=

* 2022-02-25: Written by Steven J. DeRose.
* 2022-04-07: Add --color, --ascii, --slashc. Add rest of --space alternatives.
* 2022-07-39: Add --bgcolor.

=Rights=

Copyright 2022-02-25 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See [http://creativecommons.org/licenses/by-sa/3.0/] for more information.

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""


###############################################################################
# Main
#
if __name__ == "__main__":
    import argparse
    colors = {
        "black":0, "red":1, "green":2, "yellow":3, "blue":4,
        "magenta":5, "cyan":6, "white":7, "default":9 }

    def processOptions() -> argparse.Namespace:
        try:
            from BlockFormatter import BlockFormatter
            parser = argparse.ArgumentParser(
                description=descr, formatter_class=BlockFormatter)
        except ImportError:
            parser = argparse.ArgumentParser(description=descr)

        parser.add_argument(
            "--ascii", action="store_true",
            help="Turn all non-ASCII to \\u.")
        parser.add_argument(
            "--slashc", "-c", action="store_true",
            help="If the input ends with \\c, suppress the newline (cf POSIX).")
        parser.add_argument(
            "--backslashes", "--decode", action="store_true",
            help="Recognize and decode Python-style \\x, \\u, \\n, etc.")
        parser.add_argument(
            "--bgcolor", type=str, choices=list(colors.keys()),
            help="Write in this (background) color.")
        parser.add_argument(
            "--fgcolor", "--color", type=str, choices=list(colors.keys()),
            help="Write in this (foreground) color.")
        parser.add_argument(
            "--end", type=str, metavar="S", default="\n",
            help="Write this at the end (default: newline).")
        parser.add_argument(
            "--iencoding", type=str, metavar="E", default="utf-8",
            help="Assume this character coding for input. Default: utf-8.")
        parser.add_argument(
            "--latin1", "--latin-1", action="store_true",
            help="Turn all non-Latin-1 to \\u.")
        parser.add_argument(
            "-n", action="store_true",
            help="Suppress newline (same as --end='').")
        parser.add_argument(
            "--oencoding", type=str, metavar="E", default="utf-8",
            help="Use this character coding for output. Default: iencoding.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "--showControls", "--pics", "--controls", "-c", action="store_true",
            help="Map control characters to Unicode CONTROL PICTURES for visibility.")
        parser.add_argument(
            "--showWhitespace", "-w", action="store_true",
            help="Map whitespace characters to backslashes (except regular space).")
        parser.add_argument(
            "--space", "--showSpace", "-s", type=str, default=None,
            choices=[ "LITERAL", "HEX", "UNDER", "b", "SP" ],
            help="Map the regular space character (d32, U+20) to something.")
        parser.add_argument(
            "--stderr", "-2", action="store_true",
            help="Write to STDERR instead of STDOUT.")
        parser.add_argument(
            "--unicode", action="store_const", dest="iencoding",
            const="utf8", help="Assume utf-8 for input files.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")

        parser.add_argument(
            "text", type=str, nargs=argparse.REMAINDER,
            help="What to echo.")

        args0 = parser.parse_args()

        if (args.n): args.end = ""
        if (args.space):
            if (args.space == "LITERAL"): args.spaceGoesTo = " "
            elif (args.space ==  "HEX"): args.spaceGoesTo = "\\x20"
            elif (args.space == "UNDER"): args.spaceGoesTo = chr(0x2423)
            elif (args.space ==  "b"): args.spaceGoesTo = chr(0x2422)
            elif (args.space == "SP"): args.spaceGoesTo = chr(0x2420)
            else: lg.fatal("Unknown value for --space: '%s'.", args.space)
        return(args0)


    ###########################################################################
    #
    args = processOptions()
    if (args.iencoding and not args.oencoding):
        args.oencoding = args.iencoding
    if (args.oencoding):
        # https://stackoverflow.com/questions/4374455/
        # sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stdout.reconfigure(encoding="utf-8")

    cStart = cEnd = ""
    if (args.fgcolor or args.bgcolor):
        cStart = "\x1b["
        if (args.fgcolor): cStart += "%d" % (colors[args.fgcolor] + 30)
        if (args.bgcolor): cStart += "%d" % (colors[args.ggcolor] + 40)
        cStart += "m"
        cEnd = "\x1b0m"

    ender = args.end
    for s in args.text:
        if (args.slashc):
            if (s.endswith("\\c")):
                s = s[0:-2]
                ender = ""
            else:
                ender = args.end
        if (args.backslashes):
            try:
                str(bytes(s, encoding='utf-8').decode('unicode_escape'))
            except UnicodeDecodeError as e:
                lg.error("Unable to unescape item: %s", e)
                continue
            s = s.decode('unicode_escape')
        if (args.showControls):
            s = re.sub(r"([\x00-\x1F])", lambda mat: { chr(ord(mat.group(1))+0x2400) }, s)
        if (args.ascii):
            s = re.sub(r"([\x80-])", lambda mat: { "\\u%04x" % ord(mat.group(1)) }, s)
        if (args.latin1):
            s = re.sub(r"([\u0100-])", lambda mat: { "\\u%04x" % ord(mat.group(1)) }, s)
        if (args.space):
            s = re.sub(r" ", args.spaceGoesTo, s)
        if (args.color):
            s = cStart + s + cEnd
        if (args.stderr):
            sys.stderr.write(s+ender)
        else:
            print(s, end=ender)
