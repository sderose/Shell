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

__metadata__ = {
    "title"        : "cpPP.py",
    "description"  : "cp command, but with some additions.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2021-11-09",
    "modified"     : "2021-11-09",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Description=

[unfinished]

Do file copying pretty much like `cp`, but add some features such as:

* automatic renaming to avoid conflicts

This also has the full capability of `PowerWalk.py` for selecting what to copy.

==Usage==

    cpPP.py [options] [files] [target]


=Related Commands=


=Known bugs and Limitations=

Unlike `cp`, -f and -n do not result in the ''last'' one taking effect. -n just wins.

Not all fine details of the usual `cp` options are (yet) implemented.


=To do=

* Option to append instead of overwrite.
* Option to replace only if newer.
* Options to skip if identical.
* Shorten up path printing with -v.
* -c and -x are not yet supported.

Usual `cp` options are:

X     -a    Same as -pPR options. Preserves structure and attributes of files but not
           directory structure.

X     -f    If the destination file cannot be opened, remove it and create a new file,
           without prompting for confirmation regardless of its permissions.  (The -f
           option overrides any previous -n option.)

           The target file is not unlinked before the copy.  Thus, any existing access
           rights will be retained.

X     -H    If the -R option is specified, symbolic links on the command line are fol-
           lowed.  (Symbolic links encountered in the tree traversal are not followed.)

X     -i    Cause cp to write a prompt to the standard error output before copying a
           file that would overwrite an existing file.  If the response from the stan-
           dard input begins with the character `y' or `Y', the file copy is attempted.
           (The -i option overrides any previous -n option.)

X     -L    If the -R option is specified, all symbolic links are followed.

X     -n    Do not overwrite an existing file.  (The -n option overrides any previous -f
           or -i options.)

X     -P    If the -R option is specified, no symbolic links are followed.  This is the
           default.

X     -p    Cause cp to preserve the following attributes of each source file in the
           copy: modification time, access time, file flags, file mode, user ID, and
           group ID, as allowed by permissions.  Access Control Lists (ACLs) and
           Extended Attributes (EAs), including resource forks, will also be preserved.

           If the user ID and group ID cannot be preserved, no error message is dis-
           played and the exit value is not altered.

           If the source file has its set-user-ID bit on and the user ID cannot be pre-
           served, the set-user-ID bit is not preserved in the copy's permissions.  If
           the source file has its set-group-ID bit on and the group ID cannot be pre-
           served, the set-group-ID bit is not preserved in the copy's permissions.  If
           the source file has both its set-user-ID and set-group-ID bits on, and
           either the user ID or group ID cannot be preserved, neither the set-user-ID
           nor set-group-ID bits are preserved in the copy's permissions.

X     -R    If source_file designates a directory, cp copies the directory and the
           entire subtree connected at that point.  If the source_file ends in a /, the
           contents of the directory are copied rather than the directory itself.  This
           option also causes symbolic links to be copied, rather than indirected
           through, and for cp to create special files rather than copying them as nor-
           mal files.  Created directories have the same mode as the corresponding
           source directory, unmodified by the process' umask.

           In -R mode, cp will continue copying even if errors are detected.

           Note that cp copies hard-linked files as separate files.  If you need to
           preserve hard links, consider using tar(1), cpio(1), or pax(1) instead.

X     -v    Cause cp to be verbose, showing files as they are copied.

     -X    Do not copy Extended Attributes (EAs) or resource forks.

     -c    copy files using clonefile(2)


=History=

* 2021-11-09: Written by Steven J. DeRose.


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
def fatal(msg:str) -> None: log(0, msg); sys.exit()

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
    if (args.force):
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

def doTheCopy(ipath, opath):
    if (args.preserve):
        shutil.copy2(ipath, opath)  # follow_symlinks=True ??
    else:
        shutil.copy(ipath, opath)  # follow_symlinks=True ??
    if (args.verbose): print("%s -> %s" % (ipath, opath))
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
            help="Shorthand for -pPRs.")
        parser.add_argument(
            "--followLinks", "-L", action="store_true",
            help="Follow symbolic links.")
        parser.add_argument(
            "--force", "-f", action="store_true",
            help="Copy even when the output file already exists (overwriting it).")
        parser.add_argument(
            "--ignoreCase", action="store_true",
            help="Disregard case distinctions.")
        parser.add_argument(
            "--inquire", "-i", action="store_true",
            help="Ask user first, when the output file already exists.")
        parser.add_argument(
            "--nooverwrite", "-n", action="store_true",
            help="Never overwrite (overrides -i and -f, always (unlike `cp`).")
        parser.add_argument(
            "--preserve", "-p", action="store_true",
            help="Preserve file attributes.")
        parser.add_argument(
            "--noLinks", "-P", action="store_true",
            help="Don't follow any links. Overrides -H and -L.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "-R", action="store_true",
            help="Copy recursively.")
        parser.add_argument(
            "--separator", type=str, default="_",
            help="Put this between basename and affix(es).")
        parser.add_argument(
            "--topLevelLinks", "-H", action="store_true",
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
