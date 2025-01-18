#!/usr/bin/env python3
#
# fuseVars.py: Implement environment variable as a pseudo filesystem.
# 2022-08-29: Written by Steven J. DeRose.
#
import sys
import os
import codecs
from enum import Enum
import re
import logging
from typing import Any  #, IO, Dict, List, Union
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK  #, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

lg = logging.getLogger("fuseVars.py")


__metadata__ = {
    "title"        : "fuseVars",
    "description"  : "Implement environment variable as a pseudo filesystem.",
    "rightsHolder" : "Steven J. DeRose",
    "creator"      : "http://viaf.org/viaf/50334488",
    "type"         : "http://purl.org/dc/dcmitype/Software",
    "language"     : "Python 3.7",
    "created"      : "2022-08-29",
    "modified"     : "2023-11-23",
    "publisher"    : "http://github.com/sderose",
    "license"      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__["modified"]

descr = """
=Name=
fuseVars: Implement environment variable as a pseudo filesystem.

[UNFINISHED]

=Description=

Provide a more flexible env. variable system, quickly usable from shells.

Added features?
    * Nested aggregates (that's the biggest reason)
    * More datatypes
    * Enable shared access (w/ some kind of permissions) across processes
    * Can hang metadata like tracing, mod times, etc. on variables

==Usage==

Implemented as a very rudimentary FUSE filesystem.
Everything lives in RAM (yeah, so if this process dies, your variables
go away -- can add write-through if needed).

Each variable looks like a "file", but of course there's not the usual
overhead for going to disk. Each owning process gets its own space.

Since each variable looks like a file,
a shell that's process 123 can set one like this ("$$" is the process id):

    echo "$PATH:$HOME/myStuff" > /dev/fuseVars/$$/PATH

or the slightly more convenient append (like zsh "+="):

    echo ":$HOME/myStuff" >> /dev/fuseVars/$$/PATH

In fact these would work even without fuseVars (though *using* the variables
wouldn't work normally, you'd have to redirect for that too). But it would be
slower, wouldn't clean up when processes close, and would lack fuseVars'
functionality such as tracing, additional datatypes, inheritance, etc.

More likely, one would use shell functions such as:
    fuset() {
        varName="$1"
        shift
        echo "$*" >/dev/fuseVars/$$/$1
    }

which enables:
    fuset PATH "$PATH"

and you could get it back with:
    PATH=`cat /dev/fuseVars/$$/PATH`

or of course
    `fuget PATH`

To just use these variable as $name, requires tighter integration. Because
that's not yet done, I don't see this as very useful for simple scalar
variables. But for aggregates like associative and non-associative arrays
it's more feasible -- and since shells typically don't support nested arrays
at all, if you need that it's pretty handy. It's also a heck of a lot easier
than trying to deal with shell syntax for indirected variables -- trying
to array operations on ${(P)foo} sometime.

Aggregates work just by appending keys:
    echo "foo" > /dev/fuset/123/myBigThink/keyA/keyB/2

TODO: Make sure not to confuse:
    * numeric vs. string (vs. other?) keys (/#0009 for numerics?)
    * what are allowed keys? tokens only? [^\\s/'"$]? Unicode?
    * How do we set aggregate type? insist on typeset on create?
        list, dict, set, typedList, queue, stack, deque
        (cross w/ member type)
    * How to do push/pop/ins/del/slice/splice/union....?
        [0009] [x:y] [-1]
        Avoid the JS mess!!!

Main API calls to support:
    open
    release
    read (includes seek arg)
    write (includes seek arg)
    truncate (includes len arg)
    setxattr/getxattr/listxattrs
    link stuff?
    dirs as aggregates?

ways to retrieve (encoding param?)
    localized?
    tokenized?
    visibilized?
    quoted?
    formatted per pref?
    aggregates:
        line per item
        join(delim)


=See also=

My "pez" package to support Python-like datatypes directly in zsh.

https://thepythoncorner.com/posts/2017-02-28-writing-a-fuse-filesystem-in-python/

This is modelled on an example from
https://github.com/fusepy/fusepy/tree/master/examples. It's unclear whether
modelling after use of a standard API is copyrightable at all, but in case,
the terms on that code are:

    Copyright 2012 Giorgos Verigakis

    Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

The "actual" code is, as noted below, by Steven J. DeRose.


=Known bugs and Limitations=


=To do=

* Settle on a syntax for numeric vs. string (vs. other?) keys
* Settle on a syntax for assigning datatype, incl. for aggregates
* Should some operations (union, extend, clear,...) be built in? How?
* How to clear when process ends
* What about circularity?
* Are permissions the way to do... permissions? Is a 'group' a process group?
* Persistence?
* Logging/tracing? adstop?
* What does "ls" do to get the list? opendir (=open?), readdir, (f)stat.
See [https://github.com/wertarbyte/coreutils/blob/master/src/ls.c].


=History=

* 2022-08-29: Written by Steven J. DeRose.


=Rights=

This work is by Steven J. DeRose, though as noted above, it was inspired
by some prior examples of FUSE use. I hereby place my work herein in the
Public Domain. Any parts considered to be from those prior works,
of course remain under their original terms (again, see above).

For the most recent version, see [http://www.derose.net/steve/utilities]
or [https://github.com/sderose].


=Options=
"""


###############################################################################
# TODO: Sync w/ standards?
#
class VarType(Enum):
    Any         = 0

    BOOL        = 100  # Parameterize?? tri-state?

    # Numerics
    NUMERIC     = 200  # Parameterize by unit, precision, range, conf limit???
    ordinal     = 201
    unsigned    = 202
    int         = 203
    prob        = 250
    float       = 251
    double      = 252
    complex     = 253
    tensor_n    = 254 # Parameterize by dim/shape? or move to aggregate?

    # Chrono
    EPOCH       = 300  # Parameterize by... ??? BCE/CE?
    date        = 301
    time        = 302
    datetime    = 303

    # String
    STRING      = 400  # Parameterize by encoding/lang?
    char        = 301
    token       = 302
    record      = 303  # ??? No newline seq

    # Enums
    ENUM        = 400  # Parameterize by def
    color       = 401
    effect      = 402
    colorScheme = 403
    encoding    = 404
    locale      = 405

    # Aggregates
    COLLECTION  = 500  # Parameterize for homogeneity
    list        = 501
    stack       = 502
    queue       = 503
    deque       = 504
    dict        = 510  # Parameterize by key type? (incl enum -> obj)
    set         = 520
    tensor      = 530  # Parameterize by shape


###############################################################################
#
class OneVar:
    def __init__(
        self,
        name:str,
        typ:VarType=VarType.STRING,
        val:Any=None,
        readOnly:bool=False,
        export:bool=False,
        imported:bool=False,
        pid:int=None
        ):
        """Keep all the data needed for a single variable in a single process.
        These know a bit more than typical shell variables:
            * whether they were initially inherited from a parent shell,
            * who can see/change them (experimental):
                (since this will be interface via FUSER, looks like file perms)
                user => the owning shell
                group => the parent shell
                other => child shells
            * a preferred display format can be set (via a sprintf %-code).
              (these can also be set per-type on a process).
            * changes to a specific variable(s) can be traced as they happen
            * creation, modification, and access times are tracked.
            * MAY ADD: variable that are given live to subshells, instead of
              just being copied. But that could lead to race conditions.
        """
        self.pid = pid
        self.name = name
        self.typ = typ
        self.keyTyp = None   # Collections only
        self.valTyp = None   # Collections only
        self.val = val
        self.readOnly = readOnly
        self.export = export
        self.imported = imported

        self.permissions = 0o720  # ???
        self.ctime = time.time()
        self.mtime = None
        self.atime = None

        self.traceLevel = 0
        self.format = None

    def set(self, val:Any):
        """TODO: What should happen if the type is wrong?
        """
        if (self.traceLevel > 0):
            sys.stderr.write("SET '%s':%s: '%s' -> '%s'" %
                (self.name, self.typ, self.val, val))
        self.val = val

    def get(self, val):
        self.val = val

    def isinstance(self, typ) -> bool:
        if (not isinstance(typ, list)): typ = [ typ ]
        for t in typ:
            if (self.typ == t): return True
            if (t % 100 == 0 and t < self.typ < t+99): return True
        return False


###############################################################################
#
class EnvVars:
    """Manage the set of environment variables known to one shell process.
    On creation, copy the *exported* ones from the parent (if any).
    TODO: Tweak to be an actual subclass of dict? But then what of typ?
    """
    _SAVE_DELIM_ = ","
    _ESCAPER_ = r"(\\[n\\%s])" % (_SAVE_DELIM_)
    escTable = {
        "\\n": "\n",
        "\\\\": "\\",
        "\\"+_SAVE_DELIM_: _SAVE_DELIM_
    }

    def __init__(
        self,
        pid:int,
        parentPid:int=None,
        parentVars:'EnvVars'=None
        ):
        self.pid = pid
        self.parentPid = parentPid
        self.envVars = {}
        if (parentVars):
            for k, v in parentVars.items:
                if (not v.export): continue
                self.envVars[k] = v.copy()
                self.envVars[k].imported = True
                self.envVars[k].traceLevel = 0  # TODO: Decide

    def set(self,
        name:str,
        typ:VarType=VarType.STRING,
        val:Any=None,
        ):
        sv = OneVar(name, typ, val, self.pid)
        self.envVars[name] = sv

    def get(self,
        name:str,
        dft:Any=None
        ):
        if (name in self.envVars): return self.envVars[name]
        return dft

    def isset(self,
        name:str
        ):
        return (name in self.envVars)

    def save(self, path:str):
        with codecs.open(path, "wb", encoding="utf-8") as ofh:
            for _k, v in self.envVars.items():
                ofh.write(self._SAVE_DELIM_.join(
                    (v.k, v.typ, self.sanitize(v.value)) + "\n"))

    def load(self, path:str):
        with codecs.open(path, "rb", encoding="utf-8") as ifh:
            for rec in ifh.readlines():
                n, t, v = rec.split(sep=EnvVars._SAVE_DELIM_)
                self.set(n, typ=t, val=self.unsanitize(v))

    @staticmethod
    def sanitize(s:str):
        s = s.replace("\n", "\\n")
        s = s.replace("\\", "\\\\")
        s = s.replace(EnvVars._SAVE_DELIM_, "\\"+EnvVars._SAVE_DELIM_)
        return s

    @staticmethod
    def unsanitize(s:str):
        return re.sub(EnvVars._ESCAPER_,
            lambda x: EnvVars.escTable[x.group(s)], s)


###############################################################################
#
class EnvDB:
    """A collection of any number of EnvVars collections, one per pid.
    TODO: Somebody has to remember to nuke these when the processes end.
    """
    def __init__(self):
        self.byPid = {}

    def add(
        self,
        pid:int,
        parentPid:int=None,
        parentVars:EnvVars=None
        ):
        assert pid not in self.byPid
        self.byPid[pid] = EnvVars(pid, parentPid=parentPid, parentVars=parentVars)

    def delete(self, pid:int):
        del self.byPid[pid]

    def getInherited(self, bottomPid:int, name:str) -> OneVar:
        """Work upward from the given pid, and return the first variable
        found of the given name.
        This is much like a Python ChainMap, but is tree-structured, not list-.
        """
        while (bottomPid):
            if (name in self.byPid[bottomPid]):
                return self.byPid[bottomPid].envVars[name]
            bottomPid = self.byPid[bottomPid].parentPid
        return None

    def clearDefunct(self):
        """Delete EnvVars collections for any process that no longer exist.
        This could fail is a new process with the same ID was created,
        but that seems really unlikely.
        """
        nDeleted = 0
        for pid in self.byPid:
            try:
                rc = os.kill(pid, 0)
            except ProcessLookupError:
                del self.byPid[pid]
                nDeleted += 1
        return nDeleted




###############################################################################
#
class FuseVars(LoggingMixIn, Operations):
    """An implementation of shell variables, but intended to live as a
    user-space (pseudo-) filesystem. That seems to be the easiest way to:
        * have a persistent app that shells can all talk to:
        * have fast access (no socket setup, actual file-opening,....)
        * use very familiar shell idioms (e.g. redirects)
        * be easy to hook into shell (if anybody likes it that much)
    """
    def __init__(self):
        self.vars = EnvDB()
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(
            st_mode=(S_IFDIR | 0o755),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2)

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def create(self, path, mode):
        dirs, name = os.path.split(path)
        self.files[path] = OneVar(name)
        self.fd += 1
        return self.fd

    def rename(self, old, new):
        self.data[new] = self.data.pop(old)
        self.files[new] = self.files.pop(old)

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        if (size is None or size < 0):
            return self.data[path][offset:]
        return self.data[path][offset:offset + size]

    def truncate(self, path, length, fh=None):
        # make sure extending the file fills in zero bytes
        self.data[path] = self.data[path][:length].ljust(
            length, '\x00'.encode('ascii'))
        self.files[path]['st_size'] = length

    def write(self, path, data, offset, fh):
        self.data[path] = (
            # make sure the data gets inserted at the right offset
            self.data[path][:offset].ljust(offset, '\x00'.encode('ascii'))
            + data
            # and only overwrites the bytes that data is replacing
            + self.data[path][offset + len(data):])
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)

    def unlink(self, path):
        self.data.pop(path)
        self.files.pop(path)

    ####### Basic attrs and [P]ermissions
    #
    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)
        return self.files[path]

    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    ####### Xattrs
    #
    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})
        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    ####### Links
    #
    def readlink(self, path):
        return self.data[path]

    def symlink(self, target, source):
        self.files[target] = dict(
            st_mode=(S_IFLNK | 0o777),
            st_nlink=1,
            st_size=len(source))

        self.data[target] = source

    ####### Directories
    #
    def mkdir(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFDIR | mode),
            st_nlink=2,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        self.files['/']['st_nlink'] += 1

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def rmdir(self, path):
        # with multiple level support, need to raise ENOTEMPTY if contains any files
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1


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
            "--mount", type=str,
            help="Mount point.")
        parser.add_argument(
            "--quiet", "-q", action="store_true",
            help="Suppress most messages.")
        parser.add_argument(
            "--verbose", "-v", action="count", default=0,
            help="Add more messages (repeatable).")
        parser.add_argument(
            "--version", action="version", version=__version__,
            help="Display version information, then exit.")

        parser.add_argument(
            "files", type=str, nargs=argparse.REMAINDER,
            help="Path(s) to input file(s)")

        args0 = parser.parse_args()
        return(args0)


    ###########################################################################
    #
    args = processOptions()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(FuseVars(), args.mount, foreground=True, allow_other=True)
