#!/usr/bin/env python3
#
# cpPP.py: cp command, but with some additions.
# 2021-11-09: Written by Steven J. DeRose.
#
from __future__ import print_function
import sys
import os
#import codecs
import shutil

from PowerWalk import PowerWalk, PWType

# For oddities like resource forks
isMac = (sys.platform == "darwin")

try:
    import rsrcfork
except ImportError:
    rscfork = None
    if (isMac): sys.stderr.write(
        "Warning: Seems to be MacOS, but pip 'rsrcfork' not found. Resource forks will not be handled.")

__metadata__ = {
    "title"        : "cpPP.py",
    "description"  : "cp command, but with some additions.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-11-09",
    "modified"     : "2021-11-17",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

[unfinished]

Do file copying pretty much like `cp`, but add a few features such as:

* the full capability of `PowerWalk.py` for selecting what to copy
* automatic renaming to avoid conflicts, including pulling in ancestor directory names
* limited support for Mac resource forks: they are copied

if `--resourceForks` is set;

if the pip `rsrcfork` library is found; and
if a like-named `.rsrc` file does not already exist at the target, or --force is set.

Uses Python `copy` by default (which does not preserve metadata other than permissions).
With `-p`, uses `copy2` (which "Attempts to preserve file metadata").

==Usage==

    cpPP.py [options] [files] [target]

=Related Commands=

=Known bugs and Limitations=

Unlike `cp`, -f and -n do not result in the ''last'' one taking effect. -n just wins.

Not all fine details of the usual `cp` options are (yet) implemented.

Mac resource forks and hidden file-type codes are not copied. See [https://docs.python.org/3/library/shutil.html].

=To do=

* Add detection, warning, and copying options for Mac resource forks.

See [https://pypi.org/project/rsrcfork/].
* Option to append instead of overwrite.
* Option to replace only if newer.
* Options to skip if identical.
* Shorten up path printing with -v.
* -c and -x are not yet supported.

Add remaining `cp` options:

* -X    Do not copy Extended Attributes (EAs) or resource forks.

* -c    copy files using clonefile(2)
-- See https://stackoverflow.com/questions/47945481/how-to-clone-files-with-python.
This doesn't look viable, esp. when you can just use regular `cp -c` if needed.

=History=

* 2021-11-09: Written by Steven J. DeRose.
* 2021-11-17: Rudimentary support for old Mac resource forks. Add `--newer`.

=Rights=

Copyright 2021-11-09 by Steven J. DeRose. This work is licensed under a
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
def fatal(msg:str) -> None: log(0, msg), sys.exit()

nDirsSkipped = 0

###############################################################################
# TODO: At depth>0, shouldn't need to worry about name conflicts.
#
def doOneFile(ipath:str, opath:str, depth:int=0) -> str:
    """Read and deal with one individual file.
    """
    if (os.path.islink(ipath)):                         # LINKS
        if (args.followLinks or
            (args.topLevelLinks and depth==0)):
            ipath = os.path.realpath(ipath)

    if (os.path.isdir(ipath)):                          # DIRECTORY
        if (not args.recursive):
            global nDirsSkipped
            nDirsSkipped += 1
            return
        for ch in os.listdir(ipath):
            doOneFile(os.path.join(ipath, ch), os.path.join(opath, ch), depth=depth+1)
        return

    _dirpath, basename = os.path.split(ipath)

    cand = os.path.join(opath, basename)
    if (not os.path.exists(cand)):                      # NO CONFLICT
        return doTheCopy(ipath, cand)
    if (args.nooverwrite):                              # CONFLICT
        return None
    if (args.force or (args.newer and isNewer(ipath, cand))):
        return doTheCopy(ipath, cand)
    if (args.inquire):
        print("overwrite %s? (y/n [n])" % (cand), end="")
        buf = sys.stdin.readline()
        if (buf.startswith("y") or buf.startswith("Y")):
            return doTheCopy(ipath, cand)

        return None

    cand = pulls(ipath, opath, args.maxPulls)     # RENAME TO FIX CONFLICT
    if (cand):
        return doTheCopy(ipath, cand)

    cand = serials(ipath, opath)
    if (cand):
        return doTheCopy(ipath, cand)

    raise IOError("Can't find a place to put '%s' in '%s'." % (ipath, opath))

def isNewer(path1:str, path2:str):
    """Return True iff path1 is noticeably more recently modified than path2.
    "Noticeably" means 2 seconds, due to Windows time precision issues.
    """
    mtime1 = os.path.getmtime(path1)
    mtime2 = os.path.getmtime(path2)
    return (mtime1 > mtime2+2.000)

def pulls(ipath:str, opath:str, maxPulls:int=3) -> str:
    """Try adding one ancestor dir name at a time to the basename, hoping for
    uniqueness.
    """
    parts = ipath.split("/")
    #basename = parts[-1]
    parts.pop()
    for i in reversed(range(len(parts))):
        maxPulls -= 1
        if (maxPulls < 0): return None
        obasename = args.separator.join(parts[i:])
        fullpath = os.path.join(opath, obasename)
        if (not os.path.exists(fullpath)): return fullpath
    return None

def serials(ipath:str, opath:str) -> str:
    """Try adding one ancestor dir name at a time to the basename, hoping for
    uniqueness.
    """
    _dirs, basename = os.path.split(ipath)
    fmt = "%%s%%s%%%d0d" % (args.width)
    for i in range(args.maxSerial):
        obasename = fmt % (basename, args.separator, i)
        fullpath = os.path.join(opath, obasename)
        if (not os.path.exists(fullpath)): return fullpath
    return None

def doTheCopy(ipath, opath) -> str:
    if (args.preserve):
        shutil.copy2(ipath, opath)  # follow_symlinks=True ??
    else:
        shutil.copy(ipath, opath)  # follow_symlinks=True ??
    if (args.verbose): print("%s -> %s" % (ipath, opath))

    if (args.resourceForks):
        orpath = os.path.join(opath, ".rsrc")
        if (os.path.exists(orpath) and not args.force):
            warning0("Skpping copy of resource fork to %s (target exists)." % (orpath))
            return opath
        warning1("Copying resource fork to %s." % (orpath))
        orfh = open(orpath, "wb")
        irfh = rsrcfork.open(ipath)
        for buf in irfh.read():
            orfh.write(buf)
        irfh.close()
        orfh.close()

    return opath

###############################################################################
# Main
#
if __name__ == "__main__":
    import argparse
    def anyInt(x:str) -> int:
        return int(x, 0)

    def processOptions() -> argparse.Namespace:
        try:
            from BlockFormatter import BlockFormatter
            parser = argparse.ArgumentParser(
                description=descr, formatter_class=BlockFormatter)
        except ImportError:
            parser = argparse.ArgumentParser(description=descr)

        parser.add_argument(
            "-a", action="store_true",
            help="Shorthand for -p -P -R -s.")
        parser.add_argument(
            "--followLinks", "--follow-links", "-L", action="store_true",
            help="Follow symbolic links.")
        parser.add_argument(
            "--force", "-f", action="store_true",
            help="Copy even when the output file already exists (overwriting it).")
        #parser.add_argument(
        #    "--ignoreCase", "--ignore-case", aaction="store_true",
        #    help="Disregard case distinctions.")
        parser.add_argument(
            "--inquire", "-i", action="store_true",
            help="Ask user before copying, when the output file already exists.")
        parser.add_argument(
            "--maxPulls", "--max-pulls", type=int, default=0, metavar="N",
            help="Pull up to N ancestor directory names into the filename to uniqify.")
        parser.add_argument(
            "--newer", action="store_true",
            help="Overwrite a like-named file at the target, if replacement is newer.")
        parser.add_argument(
            "--noOverwrite", "--no-overwrite""-n", action="store_true",
            help="Never overwrite (supercedes -i and -f, always (unlike `cp`).")
        parser.add_argument(
            "--noLinks", "--no-links", "-P", action="store_true",
            help="Don't follow any links. Overrides -H and -L.")
        parser.add_argument(
            "--preserve", "-p", action="store_true",
            help="Preserve file attributes. See also --resourceForks.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "-R", "--recursive", action="store_true",
            help="Copy recursively.")
        parser.add_argument(
            "--resourceForks", "--resource-forks", action="store_true",
            help="Cheeck for Mac resource forks and copy them to separate .rsrc files.")
        parser.add_argument(
            "--separator", type=str, default="_",
            help="Put this between basename and affix(es).")
        parser.add_argument(
            "--topLevelLinks", "--top-level-links", "-H", action="store_true",
            help="Follow symbolic links, but only at the top level.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")
        parser.add_argument(
            "--width", type=anyInt, metavar="N", default=4,
            help="For serial number suffixes, pad to at least this many digits.")

        PowerWalk.addOptionsToArgparse(parser)

        parser.add_argument(
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        args0 = parser.parse_args()
        if (args0.R):
            args0.recursive = True  # Let PowerWalk know
        if (args0.a):
            args0.preserve = args0.noLinks = args0.recursive = True
        if (args.noLinks):
            args0.followLinks = args0.topLevelLinks = False
        if (args.resourceForks and rsrcfork is None):
            fatal("--resourceForks requested, but pip rsrcfork library not available.")
        if (args.force and args.newer):
            fatal("--force and --newer both specified. Please pick just one of them.")
        return(args0)

    ###########################################################################
    #
    args = processOptions()

    if (len(args.files) == 0):
        fatal("cpPP.py: No files specified....")

    pw = PowerWalk(args.files, open=False, close=False,
        encoding=args.iencoding)
    pw.setOptionsFromArgparse(args)
    for path0, fh0, what0 in pw.traverse():
        if (what0 != PWType.LEAF): continue
        doOneFile(path0, args.tgtDir, depth=0)

    if (not args.quiet):
        warning0("cpPP.py: Done, %d files.\n" % (pw.getStat("regular")))
