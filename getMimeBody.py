#!/usr/bin/env python3
#
# getMimeBody.py: Extract the 'main' content of an email file.
# 2021-11-19: Written by Steven J. DeRose.
#
import sys
import os
#import codecs
import re
from typing import Dict, List  #, IO, Union
from enum import Enum

import mimetypes
from email import message_from_binary_file
from email.parser import BytesParser  #, Parser
from email.policy import default

#import string
#import math
#import subprocess
#from collections import defaultdict, namedtuple

from PowerWalk import PowerWalk, PWType
from alogging import ALogger
lg = ALogger()

__metadata__ = {
    "title"        : "getMimeBody.py",
    "description"  : " Extract the 'main' content of an email file.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-11-19",
    "modified"     : "2021-11-19",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

Given a MIME email file or the slightly-modified Apple variant, extract the
"main" content (preferring HTML over "plain" if both are there), clean it up,
and return it or send it to a browser.


==Usage==

    getMimeBody.py [options] [files]


=Related Commands=

Python's `email` library does the heavy lifting.

BytesParser() produces headers as an `email.message.EmailMessage`:
    policy
    _headers
    _unixfrom
    _payload
    _charset
    preamble
    epilogue
    defects
    _default_type

.headers is all strings. But .headers['to'], etc., have a .addresses items, which
is a list of Address objects, each of which has .username, .domain, .display_name.


=Known bugs and Limitations=


=To do=


=History=

* 2021-11-19: Written by Steven J. DeRose.


=Rights=

Copyright 2021-11-19 by Steven J. DeRose. This work is licensed under a
Creative Commons Attribution-Share-alike 3.0 unported license.
See [http://creativecommons.org/licenses/by-sa/3.0/] for more information.

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""

def log(lvl:int, msg:str) -> None:
    if (args.verbose >= lvl): sys.stderr.write(msg + "\n")
def warning0(msg:str) -> None: log(0, msg)
def warning1(msg:str) -> None: log(1, msg)
def warning2(msg:str) -> None: log(2, msg)
def error(msg:str) -> None: log(0, msg)
def fatal(msg:str) -> None: log(0, msg); sys.exit()


###############################################################################
#
# `email` lib keys them in lower case....
mainHeaders = [ 'from', 'to', 'subject', 'date', 'message-id' ]

def doOneFile(path:str) -> int:
    """Read and deal with one individual file.
    """
    if (args.headersToShow != 'none'):
        with open(path, 'rb') as fp:
            headers = BytesParser(policy=default).parse(fp)
            dumpAddresses(headers, 'from')
            dumpAddresses(headers, 'to')
            dumpAddresses(headers, 'cc')
            dumpAddresses(headers, 'bcc')
            print('Subject: %s' % (headers['subject']))
            print('Date: %s' % (headers['date']))
            print('Message-ID: %s' % (headers['message-id']))
            if (args.verbose or args.headersToShow == 'all'):
                print("\nAll other MIME headers:")
                dumpHeaders(headers, exclude=mainHeaders)

    with open(path, 'rb') as fp:
        msg = message_from_binary_file(fp, policy=default)
        for partNum, part in enumerate(msg.walk()):
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                warning1("Got multipart.")
                continue
            # Applications should really sanitize the given filename so that an
            # email message can't be used to overwrite important files
            thisType = part.get_content_type()
            thisPart = part.get_payload(decode=True)
            fmtPart = formatBody(thisPart)

            print("\n======= Part %d (%s):" % (partNum, thisType))
            print(fmtPart)
            if (args.saveParts):
                filename = part.get_filename()
                if not filename:
                    ext = mimetypes.guess_extension(thisType)
                    if not ext: ext = '.bin'
                    filename = f'part-{partNum:03d}{ext}'
                if (os.path.exists(filename)):
                    error("Output file already exists: '%s'." % (filename))
                    continue

def dumpAddresses(headers:Dict, which:str) -> None:
    header = headers[which]
    if (not header): return
    print(which.title()+':')  # %s' % (header))
    for _i, addr in enumerate(header.addresses):
        #warning0("  %2d: %-8s %s" % (i, type(addr).__name__, addr))
        print("    %-12s  %-16s  %-24s  %s" %
            (addr.username, addr.domain, addr.display_name, addr))

def dumpHeaders(headers:Dict, exclude:List=None) -> None:
    buf = ""
    for k, v in headers.items():
        if (exclude and k.lower() in exclude): continue
        buf += "\n    %-24s  %-24s  %s" % (k, type(v).__name__, v)
    #warning0("BytesParser produced a '%s':%s\n" % (type(headers), buf))
    print(buf[1:])

def formatBody(doc:str):
    if (args.bodyForm == "none"):
        return ""
    elif (args.bodyForm == "plain"):
        return doc
    elif (args.bodyForm == "pp" or args.bodyForm == "clean" ):
        doc = runTidy(doc)
        if (re.search(r"\\n", doc)):
            warning0("escaped newline(s) in body")
            doc = re.sub(r"\\n", "\n", doc)
        if (args.bodyForm == "pp"): return doc
        return cleanup(doc)
    else:
        raise ValueError("--bodyForm '%s' not recognized." % (args.bodyForm))

DocType = str
AutoBool = bool
TagNames = list
Encoding = str
AUTO = None
tidyOptions = {
    # optionName                    ( type, default )
    "add-xml-decl":                 ( bool, False ),
    "add-xml-space":                ( bool, False ),
    "alt-text":                     ( str,  "" ),
    "anchor-as-name":               ( bool, True ),
    "assume-xml-procins":           ( bool, False ),
    "bare":                         ( bool, False ),
    "clean":                        ( bool, False ),
    "css-prefix":                   ( str,  "" ),
    "decorate-inferred-ul":         ( bool, False ),
    "doctype":                      ( DocType, AUTO ),
    "drop-empty-paras":             ( bool, True ),
    "drop-font-tags":               ( bool, False ),
    "drop-proprietary-attributes":  ( bool, False ),
    "enclose-block-text":           ( bool, False ),
    "enclose-text":                 ( bool, False ),
    "escape-cdata":                 ( bool, False ),
    "fix-backslash":                ( bool, True ),
    "fix-bad-comments":             ( bool, True ),
    "fix-uri":                      ( bool, True ),
    "hide-comments":                ( bool, False ),
    "hide-endtags":                 ( bool, False ),
    "indent-cdata":                 ( bool, False ),
    "input-xml":                    ( bool, False ),
    "join-classes":                 ( bool, False ),
    "join-styles":                  ( bool, True ),
    "literal-attributes":           ( bool, False ),
    "logical-emphasis":             ( bool, False ),
    "lower-literals":               ( bool, True ),
    "merge-divs":                   ( AutoBool, AUTO ),
    "merge-spans":                  ( AutoBool, AUTO ),
    "ncr":                          ( bool, True ),
    "new-blocklevel-tags":          ( TagNames, None ),
    "new-empty-tags":               ( TagNames, None ),
    "new-inline-tags":              ( TagNames, None ),
    "new-pre-tags":                 ( TagNames, None ),
    "numeric-entities":             ( bool, False ),
    "output-html":                  ( bool, False ),
    "output-xhtml":                 ( bool, False ),
    "output-xml":                   ( bool, False ),
    "preserve-entities":            ( bool, False ),
    "quote-ampersand":              ( bool, True ),
    "quote-marks":                  ( bool, False ),
    "quote-nbsp":                   ( bool, True ),
    "repeated-attributes":          ( Enum, "keep-last" ),
    "replace-color":                ( bool, False ),
    "show-body-only":               ( AutoBool, False ),
    "uppercase-attributes":         ( bool, False ),
    "uppercase-tags":               ( bool, False ),
    "word-2000":                    ( bool, False ),

    # Diagnostics Options
    "accessibility-check":          ( Enum, 0 ),  # (Tidy Classic)
    "show-errors":                  ( int,  6 ),
    "show-warnings":                ( bool, True ),

    # Pretty Print Options
    "break-before-br":              ( bool, False ),
    "indent":                       ( AutoBool, False ),
    "indent-attributes":            ( bool, False ),
    "indent-spaces":                ( int,  2 ),
    "markup":                       ( bool, True ),
    "punctuation-wrap":             ( bool, False ),
    "sort-attributes":              ( Enum, None ),
    "split":                        ( bool, False ),
    "tab-size":                     ( int,  8 ),
    "vertical-space":               ( bool, False ),
    "wrap":                         ( int,  68 ),
    "wrap-asp":                     ( bool, True ),
    "wrap-attributes":              ( bool, False ),
    "wrap-jste":                    ( bool, True ),
    "wrap-php":                     ( bool, True ),
    "wrap-script-literals":         ( bool, False ),
    "wrap-sections":                ( bool, True ),

    # Character Encoding Options
    "ascii-chars":                  ( bool, False ),
    "char-encoding":                ( Encoding, "ascii" ),
    "input-encoding":               ( Encoding, "latin1" ),
    "language":                     ( str,  "" ),
    "newline":                      ( Enum, "" ),  # Platform dependent
    "output-bom":                   ( AutoBool, "auto" ),
    "output-encoding":              ( Encoding, "ascii" ),

    # Miscellaneous Options
    "error-file":                   ( str,  "" ),
    "force-output":                 ( bool, False ),
    "gnu-emacs":                    ( bool, False ),
    "gnu-emacs-file":               ( str,  "" ),
    "keep-time":                    ( bool, False ),
    "output-file":                  ( str,  "" ),
    "quiet":                        ( bool, False ),
    "slide-style":                  ( str,  "" ),
    "tidy-mark":                    ( bool, True ),
    "write-back":                   ( bool, False  ),
}

def runTidy(doc) -> str:
    """See http://tidy.sourceforge.net/docs/quickref.html
    """
    from tidylib import tidy_document
    # This returns bytes, not str....
    doc, _errors = tidy_document(doc, options={
        # See above for full option list.
        "numeric-entities": 1,
        "indent": 1,
        "tidy-mark": 0,        # No tidy meta tag in output
        "wrap": 0,             # No wrapping
        "alt-text": "",
        "doctype": 'strict',
        "force-output": 1,     # May not get what you expect but you will get something
        #"drop-empty-paras": 1
        })
    doc = str(doc, encoding="utf-8")
    return doc

flags = re.DOTALL|re.UNICODE

def cleanup(doc):
    doc = re.sub(r"<meta .*?>", "", doc, flags=flags)
    doc = re.sub(r"<style .*?</style>\s+", "", doc, flags=flags)
    doc = re.sub(r"(<\w+) class=\"MsoNormal\"", "<\\1", doc, flags=flags)
    # doc = re.sub(r"(<p.*>\s+)", "\\1", doc, flags=re.DOTALL)
    # doc = re.sub(r"\s+</p>", "</p>", doc)
    doc = nukeWhitespaceElements(doc)
    return doc

wsExpr = r"(\s|\xA0|&#0*160;|&#X0*A0;)*"
wsElem = r"<(\w+).*?>%s</\1\s*>\n*" % (wsExpr)

def nukeWhitespaceElements(doc:str, changeTo="<p />") -> str:
    """Match and reduce elements only containing whitespace, even if entified.
    Outlook prduces a lot of"  <p class="MsoNormal">&#160;</p>
    """
    return re.sub(wsElem, changeTo, doc, flags=flags)


###############################################################################
# Main
#
if __name__ == "__main__":
    import argparse

    def processOptions() -> argparse.Namespace:
        try:
            from BlockFormatter import BlockFormatter
            parser = argparse.ArgumentParser(
                description=descr, formatter_class=BlockFormatter)
        except ImportError:
            parser = argparse.ArgumentParser(description=descr)

        parser.add_argument(
            "--bodyForm", type=str, default="pp",
            choices=[ "none", "plain", "pp", "clean" ],
            help="Which header fields to diplsay.")
        parser.add_argument(
            "--headersToShow", type=str, default="main",
            choices=[ "none", "main", "all" ],
            help="Which header fields to diplsay.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "--saveParts", action="store_true",
            help="Save the message parts somewhere (unfinished).")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")

        PowerWalk.addOptionsToArgparse(parser)

        parser.add_argument(
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        args0 = parser.parse_args()
        return(args0)


    ###########################################################################
    #
    args = processOptions()

    if (len(args.files) == 0):
        fatal("getMimeBody.py: No files specified....")

    pw = PowerWalk(args.files, open=False, close=False)
    pw.setOptionsFromArgparse(args)
    for path0, fh0, what0 in pw.traverse():
        if (what0 == PWType.LEAF): doOneFile(path0)
    if (not args.quiet):
        warning0("getMimeBody.py: Done, %d files.\n" % (pw.getStat("regular")))
