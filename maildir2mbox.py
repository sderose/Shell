#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# maildir2mbox.py
#
import sys
import os
import argparse

import mailbox
import email

__metadata__ = {
    'title'        : "maildir2mbox.py",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2013-05-06",
    'modified'     : "2020-03-01",
    'publisher'    : "http://github.com/sderose",
}
__version__ = __metadata__['modified']

descr = """
=Description=

Convert a MacOSX email directory, to `mbox` files.


=History=

* 2013-05-06: Adapted by Steven J. DeRose, from maildir2mbox.py by
Frédéric Grosshans, 19 January 2012 and
Nathan R. Yergler, 6 June 2010. See
[http://yergler.net/blog/2010/06/06/batteries-included-or-maildir-to-mbox-again].
* 2015-09-19: Cleanup, sjdUtils, MarkupHelpFormatter, etc.
* 2018-11-07: Update to Python 3.
* 2020-03-01: Layout and lint.


=To do=

* Add other Python-supported mail formats (MH, Babyl, MMDF)
* Maybe add Mac Mail format? (@10.4, changed from mbox to "emix").
http://en.wikipedia.org/wiki
Comparison_of_email_clients#Database.2C_folders_and_customization
http://email.about.com/od/macosxmailaddons/gr/emlx_to_mbox.htm
* Or just "Save As" "Raw Message Source".


=Doc from original version=

maildir2mbox.py: Find and convert
all the Evolution mailboxes to Thurderbird.
Note: Evolution's mail data is mostly in hidden directories,
commonly under ~/.local/share/evolution/mail/local/.Sent/{cur|new|tmp}/*.
This script should find all that are under the starting point.
See also https://freeshell.de//~kaosmos/mboximport-en.html

=Background=

    Frédéric Grosshans, 19 January 2012
    Nathan R. Yergler, 6 June 2010

This file does not contain sufficient creative expression to invoke
assertion of copyright. No warranty is expressed or implied; use at
your own risk.

---

Uses Python's included mailbox library to convert mail archives from
maildir [http://en.wikipedia.org/wiki/Maildir] to
mbox [http://en.wikipedia.org/wiki/Mbox] format, including subfolders.

See http://docs.python.org/library/mailbox.html#mailbox.Mailbox for
full documentation on this library.

---

To run, save as md2mb.py and run:

$ python md2mb.py [maildir_path] [mbox_filename]

[maildir_path] should be the the path to the actual maildir (containing new,
cur, tmp, and the subfolders, which are hidden directories with names like
.subfolde.subsubfolder.subsubsbfolder);

[mbox_filename] will be newly created, as well as a [mbox_filename].sbd the
directory.


=Options=
"""


###############################################################################
#
def warning(msg):
    sys.stderr.write(msg + "\n")
    return()


###############################################################################
#
def maildir2mailbox(maildirname, mboxfilename):
    """Convert a MacOSX email directory, to `mbox` files.
    """
    # open the existing maildir and the target mbox file
    maildir = mailbox.Maildir(maildirname, email.message_from_file)
    if (not maildir):
        warning("Can't open maildir from '%s'." % (maildirname))
        sys.exit()
    nMessages = maildir.__len__()
    warning("Opened maildir '%s', messages: %d." % (maildirname, nMessages))

    mboxfile = mailbox.mbox(mboxfilename, create=True)
    if (mboxfile is None):
        warning("Can't open mboxfile from '%s'."% (mboxfilename))
        sys.exit()
    warning("Opened output mbox '%s', messages: %d." %
        (mboxfilename, mboxfile.__len__()))

    if (args.test):
        warning("Would convert '%s' to '%s'." % (maildirname, mboxfilename))
        return(0)

    # lock the mbox
    mboxfile.lock()

    # iterate over messages in the maildir and add to the mbox
    recnum = 0
    for msg in maildir:
        recnum += 1
        if (args.tickInterval and (recnum % args.tickInterval==0)):
            warning("Processing message %d of %d." % (recnum, nMessages))
        mboxfile.add(msg)

    # close and unlock
    mboxfile.close()
    maildir.close()
    return(recnum)


###############################################################################
# Process options
#
try:
    from BlockFormatter import BlockFormatter
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=BlockFormatter)
except ImportError:
    parser = argparse.ArgumentParser(description=descr)

parser.add_argument(
    "--maildirpath", type=str, metavar="path", default=".",
    help='A maildir (containing new, cur, tmp, etc. (usually hidden)')
parser.add_argument(
    "--mboxpath", type=str, metavar="path",
    default=os.environ["HOME"] + "/mailConverted",
    help='Where to put the resulting mbox file.')
parser.add_argument(
    "--quiet", "-q", action='store_true',
    help='Suppress most messages.')
parser.add_argument(
    "--test", action='store_true',
    help='Just find the mailboxes, don\'t convert.')
parser.add_argument(
    "--tickInterval", type=int, metavar='N', default=100,
    help='Report progress every n records.')
parser.add_argument(
    "--verbose", action='count', default=0,
    help='Add more messages (repeatable).')
parser.add_argument(
    "--version", action='version', version='Version of '+__version__,
    help='Display version information, then exit.')

args = parser.parse_args()

if (not os.path.isdir(args.maildirpath)):
    warning("maildir directory not found: '%s'." % (args.maildirpath))
    sys.exit()


###############################################################################
# Main
#
dirname = args.maildirpath
mboxname = args.mboxpath
if (not os.path.isdir(mboxname)):
    warning("Cannot find mailbox at '%s'." % (mboxname))
    sys.exit()

warning(dirname +' -> ' +mboxname)

mboxdirname = mboxname+'.sbd'
if not os.path.exists(mboxdirname):
    os.makedirs(mboxdirname)
maildir2mailbox(dirname, mboxname)

listofdirs = []
for dirpath, dirnames, filenames in os.walk(dirname):
    dn = os.path.basename(dirpath)
    if dn in ['new', 'cur', 'tmp']: continue  # TODO: not aggressive enough
    listofdirs = dirpath

if (args.text):
    for curDir in listofdirs:
        warning("Would do " + curDir)
    sys.exit(0)

for curDir in listofdirs:
    curlist=[mboxname]+curDir.split(sep='.')
    curpath=os.path.join(*[dn+'.sbd' for dn in curlist if dn])
    if not os.path.exists(curpath):
        os.makedirs(curpath)
    warning('| ' +curDir +' -> '+curpath[:-4])
    maildir2mailbox(os.path.join(dirname,curDir),curpath[:-4])

if (not args.quiet):
    warning("Done.")

sys.exit(0)
