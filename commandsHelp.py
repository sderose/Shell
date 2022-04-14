#!/usr/bin/env python3
#
# commandsHelp.py
#
# <2018-04: Written by Steven J. DeRose.
#
# To do:
#
from __future__ import print_function
import sys

__metadata__ = {
    'title'        : "commandsHelp.py",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2018-04-02",
    'modified'     : "2020-03-03",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr = """
==A brief summary of essential Linux commands=

When you log in to a Unix, Linux, or Mac OS X terminal session, you're
talking to a program called "the shell", which interprets your typed
commands and sends them to other programs as needed. There are many
different shell programs available, but you'll almost certainly be
using one called "bash".

Linux commands start with a single word (no spaces, and rarely any
characters but a-z, and an occasional capital, digit, hyphen, underscore,
plus, or period.

Most then permit various "options", which almost always start with one
or two hyphens, an option name, and sometimes a value:

The command to see the list of files in the current directory is "ls",
and it has many, many options:

    ls
    ls -l        more detail
    ls -a        include files whose names start with "."
    ls -l fil*   details, but only for files whose names start with "fil"
    ls -d        list, but for directories list them not their contents

After the options, many commands take a list of one or more files.

You can usually stop a running command with control-C.

===List of the most crucial commands===

    man          see the manual
    more         see a file ('man' typically uses 'more' as its viewer)
    less         a better version of 'more'

    pwd          see what current (=working) directory you're at
    cd           change to a different working directory
    ls           list files
    chmod        change who can read/write/run a file
    rm           remove files (no trash can!)
    mv           move a file (quietly overwrites destination!)
                     (moving includes renaming)
    cp           copy a file (quietly overwrites destination!)
    mkdir        Make a new directory
    rmdir        Remove a directory (must already be empty)
    grep         Search file(s) for matches to a regex
    find         Search under a directory for files (see 'man')
    locate       Search for a file by name

===Editing===

You'll often want to edit text files for one reason or another. Many
editors are available, such as:

    emacs         A powerful but complex editor, highly customizable.
                  Heavy on control keys (similar to bash command-editing).
    vim           A pain to learn, but once you do you can go really fast.
    nano          A bare-bones text editor, also control-key oriented.
    gedit         Sort of a "Notepad" style editor.
    nedit         Basic GUI-ish editor.
    kate          Free, high-function.

Once you pick one you like, you can tell Linux programs to use that one
if they start up an editor for you. To do that, go into your .bashrc
or .bash_profile file, and add a line like:
    export EDITOR="nedit"


===Getting help===

"man" or sometimes "info" plus the command name, will get you the
manual information on a command (if any). In the "man" viewer, you
can move around with many single-character commands.
As it says at the bottom of the screen, use "q" to quit, "h" for help.

===Moving around===

You're always in some directory (=folder). You can see which one with:

    pwd

Directories are separated by "/", and you can moved (=change) to one with
"cd" plus the "path" to the place you want:

    cd /home/john/Projects/nlp

There are some special conventions for referring to places in the
file system via paths:

    A path *starting* with "/" is "absolute", meaning it begins at the very
top of the file-system hierarchy.
A path starting with "~" is relative to your home directory (which is usually
at "/home/" plus your user-id).
Other paths begin at the current directory, which can also be referred to
as ".".

    cd /var/log
    cd ~/Projects/nlp
    cd ./myProgs/Java/

Files are referred to just like directories (in fact, on Linux a directory
is just a special file, that lists what other files are in it).

It usually doesn't matter whether you put "/" on the end or not, when
referring to a directory. But sometimes it does.

The "ls" command mentioned earlier, provides a list of the specified files.
Like most commands, it can take specific filenames, paths, or even "globs",
which are paths with regex-like characters:

    ls /var/log/a*


===Working the Command Line===

You can do a fair amount of editing while typing commands.
Backspace works, but so do left and right arrow keys.

The up and down arrow keys let you go back through the history of commands
you've done recently; once you find one you want to do, just press RETURN;
or edit it and then press RETURN. You can also search back through the history
with ^R (control+R).

Other control keys work, too; and they work in many other places (including
in most typing boxes and forms on Macs, PCs, and Linux:

    ^d     Delete current character
    ^k     Delete (=kill) to end of line
    ^w     Delete to start of word
    ESC d  Delete to end of word
    ^y     Paste (=yank) whatever was last killed/cut.
    ESC ^y Paste-previous (=yank-pop) -- replace paste with prior cut...
    ^a     Move to start of line
    ^e     Move to end of line
    TAB    Auto-complete a command or file name
               TAB again to see a list of multiple potential completions)
    ^i     Same as TAB
    ^p     Same as up-arrow (=previous)
    ^n     Same as down-arrow (=next)
    ^f     Same as right-arrow (=forward)
    ^b     Same as left-arrow (=back)
    ^t     Swap (=transpose) current character with previous

A couple other control keys are also important:
    ^c     Stop a running program
    ^z     Suspect a running program; you can resume it with "bg"
    ~      In filenames, replaced by the path to your home directory

===Characters and Punctuation===

Built-in Linux commands are almost all ignorant of Unicode, so don't count
on them for non-uniformly-English data unless you check.

Linux uses almost all the punctuation marks for special things, so it's
a good idea to keep them out of file names. Many are used like regexes
(but not *quite* the same, and called "globs"), for specifying groups of
files or directories to work on:

    *         any sequence of characters (like regex ".*", NOT "*"!)
    [a-eA-E]  any character from the set
    [^x]      any character not in the set.

Period is mainly used to separate the "base filename" from the "extension",
where the latter identifies the kind of file: txt, csv, jpeg, html,....
It does *not* have the usual regex "match any one character" meaning
(except, of course, within actual regexes).

===Managing files===

    rm <files>    remove (there is no trash can!)
    rm -r
    rmdir <dirs>  remove an empty directory

===Customizing===

If you find yourself doing a certain command very often, particularly
with a certain bunch of options, you'll want to make an abbreviation for it.
The most trivial way is by creating an "alias", that maps a (possibly new)
command name to something:

    alias ls="ls -lF"
    alias more="less"

This works pretty much as you'd expect. If you later want to use the command
as it was (rather than the alias), use "command" in front:<
    command ls ...

The other way is called "shell functions", which can do a lot more, but
are also more complicated. Look them up sometime.

If you want aliases or shell functions to be there every time you're on,
put the lines that define them into the .bashrc or .bash_profile file in
your home directory (remember that files starting with "." don't show up
unless you use "ls -a" instead of just "ls"). A file the shell is supposed
to be able to execute, should have this as its first line:

    #!/bin/bash

You can instead put your aliases and shell function in some other file,
and pull that in from a single line in your .bashrc or .bash_profile, like:

    source ~/Documents/myAliases
"""

###############################################################################
# Process options
#
import argparse
parser = argparse.ArgumentParser(
    description="A utility by Steven J. DeRose.",
    epilog="(see also 'perldoc "+sys.argv[0]+"')"
)
parser.add_argument(
    "--verbose", action='count', default=0,
    help='Add more messages (repeatable).')
parser.add_argument(
    "--version", action='version', version='Version of '+__version__,
    help='Display version information, then exit.')

args = parser.parse_args()

print(descr)

sys.exit(0)
